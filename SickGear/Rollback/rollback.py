# SickGear Rollback Module

import os
import stat

from sickbeard import db, common
from sickbeard import encodingKludge as ek
from sickbeard.helpers import copyFile


class RollbackBase:
    def __init__(self, dbname):
        self.db_versions = {}
        self.db_name = dbname
        self.my_db = db.DBConnection(self.db_name)
        self.filename = db.dbFilename(self.db_name)
        self.backup_filename = db.dbFilename(self.db_name, 'bak')

    def _delete_file(self, path_file):
        if self._chmod_file(path_file):
            try:
                os.remove(path_file)
                if not ek.ek(os.path.isfile, path_file):
                    return True
            except (StandardError, Exception):
                pass

    @staticmethod
    def _chmod_file(path_file):
        if ek.ek(os.path.isfile, path_file):
            file_attribute = ek.ek(os.stat, path_file)[0]
            if not file_attribute & stat.S_IWRITE:
                # file is read-only, so make it writeable
                try:
                    ek.ek(os.chmod, path_file, stat.S_IWRITE)
                    file_attribute = ek.ek(os.stat, path_file)[0]
                except OSError:
                    pass
            if file_attribute & stat.S_IWRITE:
                return True

    def make_backup(self):
        copyFile(self.filename, self.backup_filename)

    def remove_backup(self):
        self._delete_file(self.backup_filename)

    def restore_backup(self):
        if (ek.ek(os.path.isfile, self.backup_filename) and
                ek.ek(os.path.isfile, self.filename)):
            if self._delete_file(self.filename):
                copyFile(self.backup_filename, self.filename)
                self.remove_backup()

    def remove_table(self, name):
        if self.my_db.hasTable(name):
            self.my_db.action('DROP TABLE' + ' [%s]' % name)

    def remove_index(self, table, name):
        if self.my_db.hasIndex(table, name):
            self.my_db.action('DROP INDEX' + ' [%s]' % name)

    def set_db_version(self, version):
        self.my_db.mass_action([['UPDATE' + ' db_version SET db_version = ?', [version]], ['VACUUM']])

    def run(self, rollback_version):
        self.make_backup()
        try:
            c_version = self.my_db.checkDBVersion()
            if isinstance(rollback_version, (int, long)):
                if rollback_version < c_version and c_version in self.db_versions:
                    while True:
                        if c_version not in self.db_versions:
                            break
                        self.db_versions[c_version]()
                        c_version = self.my_db.checkDBVersion()
                        if rollback_version >= c_version:
                            break
                if rollback_version == c_version:
                    self.remove_backup()
                    return True
            self.restore_backup()
        except (StandardError, Exception):
            self.restore_backup()
        return False


class FailedDb(RollbackBase):
    def __init__(self):
        RollbackBase.__init__(self, dbname='failed.db')


class CacheDb(RollbackBase):
    def __init__(self):
        RollbackBase.__init__(self, dbname='cache.db')
        self.db_versions = {
            3: self.rollback_3,
            4: self.rollback_4,
        }

    def rollback_4(self):
        self.remove_table('providererrors')
        self.remove_table('providererrorcount')
        self.remove_table('provider_fails')
        self.remove_table('provider_fails_count')

        self.set_db_version(3)

    def rollback_3(self):
        if not self.my_db.hasTable('scene_exceptions'):
            self.my_db.action('CREATE TABLE scene_exceptions (exception_id INTEGER PRIMARY KEY, '
                              + 'indexer_id INTEGER KEY, show_name TEXT, season NUMERIC, custom NUMERIC)')

        if not self.my_db.hasTable('scene_exceptions_refresh'):
            self.my_db.action('CREATE TABLE scene_exceptions_refresh (list TEXT PRIMARY KEY, '
                              + 'last_refreshed INTEGER)')

        self.remove_table('backlogparts')
        self.remove_table('lastrecentsearch')
        self.set_db_version(2)


class MainDb(RollbackBase):
    def __init__(self):
        RollbackBase.__init__(self, 'sickbeard.db')
        self.db_versions = {
            20004: self.rollback_20004,
            20005: self.rollback_20005,
            20006: self.rollback_20006,
            20007: self.rollback_20007,
            20008: self.rollback_20008,
        }

    def rollback_20008(self):
        self.remove_table('webdl_types')

        self.set_db_version(20007)

    def rollback_20007(self):
        self.remove_table('tv_episodes_watched')

        self.set_db_version(20006)

    def rollback_20006(self):
        self.remove_index('tv_episodes', 'idx_tv_ep_ids')

        sql_result = self.my_db.select('SELECT rowid, quality FROM history WHERE action LIKE "%%%02d"' %
                                       common.SNATCHED_PROPER)

        cl = []
        for s in sql_result:
            cl.append(['UPDATE history SET action = ? WHERE rowid = ?',
                       [common.Quality.compositeStatus(common.SNATCHED, int(s['quality'])), s['rowid']]])
        if cl:
            self.my_db.mass_action(cl)

        self.remove_table('flags')
        self.set_db_version(20005)

    def rollback_20005(self):
        self.remove_table('tv_shows_not_found')
        self.set_db_version(20004)

    def rollback_20004(self):
        if self.my_db.hasTable('indexer_mapping'):
            self.my_db.mass_action([
                ['ALTER TABLE'
                 + ' indexer_mapping RENAME TO tmp_indexer_mapping'],
                ['CREATE TABLE'
                 + ' indexer_mapping (indexer_id INTEGER, indexer NUMERIC, mindexer_id INTEGER,'
                 + ' mindexer NUMERIC, PRIMARY KEY (indexer_id, indexer))'],
                ['DELETE FROM'
                 + ' tmp_indexer_mapping WHERE mindexer NOT IN (1,2)'],
                ['INSERT OR REPLACE INTO'
                 + ' indexer_mapping SELECT indexer_id, indexer, mindexer_id, mindexer FROM tmp_indexer_mapping'],
                ['DROP TABLE'
                 + ' tmp_indexer_mapping']
            ])

        if self.my_db.hasColumn('info', 'last_run_backlog'):
            self.my_db.mass_action([
                ['ALTER TABLE'
                 + ' info RENAME TO tmp_info'],
                ['CREATE TABLE'
                 + ' info (last_backlog NUMERIC, last_indexer NUMERIC, last_proper_search NUMERIC)'],
                ['INSERT OR REPLACE INTO'
                 + ' info SELECT last_backlog, last_indexer, last_proper_search FROM tmp_info'],
                ['DROP TABLE'
                 + ' tmp_info']
            ])

        my_cache_db = db.DBConnection('cache.db')
        if 0 == my_cache_db.checkDBVersion():
            from sickbeard.databases import cache_db
            db.upgradeDatabase(my_cache_db, cache_db.InitialSchema)

        if self.my_db.hasTable('scene_exceptions'):
            sql_results = self.my_db.action('SELECT *' + ' FROM scene_exceptions')
            cs = []
            for r in sql_results:
                cs.append(
                    ['INSERT OR REPLACE INTO'
                     + ' scene_exceptions (exception_id, indexer_id, show_name, season, custom)'
                     + ' VALUES (?,?,?,?,?)', [
                        r['exception_id'], r['indexer_id'], r['show_name'], r['season'], r['custom']]])

            if 0 < len(cs):
                my_cache_db.mass_action(cs)

            self.remove_table('scene_exceptions')

        self.remove_table('scene_exceptions_refresh')

        self.set_db_version(20003)
