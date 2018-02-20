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

    def is_test_db(self):
        return 100000 <= self.my_db.checkDBVersion()

    def run(self, rollback_version):
        self.make_backup()
        try:
            c_version = self.my_db.checkDBVersion()
            base_db_is_test = self.is_test_db()
            if isinstance(rollback_version, (int, long)):
                if (rollback_version < c_version or base_db_is_test) and c_version in self.db_versions:
                    while True:
                        if c_version not in self.db_versions:
                            break
                        self.db_versions[c_version]()
                        c_version = self.my_db.checkDBVersion()
                        if rollback_version >= c_version or base_db_is_test:
                            break
                if base_db_is_test:
                    if not self.is_test_db():
                        self.remove_backup()
                        return True
                elif rollback_version == c_version:
                    self.remove_backup()
                    return True
            self.restore_backup()
        except (StandardError, Exception):
            self.restore_backup()
        return False


class FailedDb(RollbackBase):
    def __init__(self):
        RollbackBase.__init__(self, dbname='failed.db')
        self.db_versions = {
            # standalone test db rollbacks (db version >=100.000)
            100000: self.rollback_test_100000,
            # regular db rollbacks
        }

    # standalone test db rollbacks (always rollback to a production db)
    def rollback_test_100000(self):
        self.my_db.mass_action([['ALTER TABLE history RENAME TO backup_history'],
                                ['CREATE TABLE history (date NUMERIC, size NUMERIC, release TEXT, provider TEXT, '
                                 'old_status NUMERIC, showid NUMERIC, season NUMERIC, episode NUMERIC)'],
                                ['REPLACE INTO history (date, size, release, provider, old_status, showid, '
                                 'season, episode) SELECT date, size, release, provider, old_status, showid, '
                                 'season, episode FROM backup_history WHERE indexer IN (0,1,2)'],
                                ['DELETE FROM backup_history WHERE indexer IN (0,1,2)'],
                                ])
        self.set_db_version(1)


class CacheDb(RollbackBase):
    def __init__(self):
        RollbackBase.__init__(self, dbname='cache.db')
        self.db_versions = {
            # standalone test db rollbacks (db version >=100.000)
            100000: self.rollback_test_100000,
            # regular db rollbacks
            3: self.rollback_3,
            4: self.rollback_4,
        }

    # standalone test db rollbacks (always rollback to a production db)
    def rollback_test_100000(self):
        self.my_db.mass_action([['DROP TABLE provider_cache'],
                                ['CREATE TABLE provider_cache (provider TEXT ,name TEXT, season NUMERIC, '
                                 'episodes TEXT, indexerid NUMERIC, url TEXT UNIQUE, time NUMERIC, quality TEXT, '
                                 'release_group TEXT, version NUMERIC)']
                                ])
        self.set_db_version(4)  # set production db version

    # regular db rollbacks
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
            # test db's
            100000: self.rollback_100000,
            100001: self.rollback_100001,
            100002: self.rollback_100001,
            # regular db's
            20004: self.rollback_20004,
            20005: self.rollback_20005,
            20006: self.rollback_20006,
            20007: self.rollback_20007,
            20008: self.rollback_20008,
            20009: self.rollback_20009,
        }

    def rollback_100001(self):
        self.remove_table('tv_episodes_watched')

        self.set_db_version(20008)

    # standalone test db rollbacks (always rollback to a production db)
    def rollback_100000(self):
        self.remove_index('tv_episodes', 'idx_tv_episodes_unique')

        self.remove_index('tv_episodes', 'idx_tv_episodes_showid_airdate')
        self.my_db.mass_action([['CREATE TABLE backup_tv_episodes (episode_id INTEGER PRIMARY KEY, showid NUMERIC, '
                                 'indexerid NUMERIC, indexer NUMERIC, name TEXT, season NUMERIC, episode NUMERIC, '
                                 'description TEXT, airdate NUMERIC, hasnfo NUMERIC, hastbn NUMERIC, status NUMERIC, '
                                 'location TEXT, file_size NUMERIC, release_name TEXT, subtitles TEXT, '
                                 'subtitles_searchcount NUMERIC, subtitles_lastsearch TIMESTAMP, is_proper NUMERIC, '
                                 'scene_season NUMERIC, scene_episode NUMERIC, absolute_number NUMERIC, '
                                 'scene_absolute_number NUMERIC, release_group TEXT, version NUMERIC)'],
                                ['REPLACE INTO backup_tv_episodes (episode_id, showid, indexerid, indexer, name, '
                                 'season, episode, description, airdate, hasnfo, hastbn, status, location, file_size, '
                                 'release_name, subtitles, subtitles_searchcount, subtitles_lastsearch, is_proper, '
                                 'scene_season, scene_episode, absolute_number, scene_absolute_number, release_group, '
                                 'version) SELECT episode_id, showid, indexerid, indexer, name, season, episode, '
                                 'description, airdate, hasnfo, hastbn, status, location, file_size, release_name, '
                                 'subtitles, subtitles_searchcount, subtitles_lastsearch, is_proper, scene_season, '
                                 'scene_episode, absolute_number, scene_absolute_number, release_group, version '
                                 'FROM tv_episodes WHERE indexer NOT IN (1,2)'],
                                ['DELETE FROM tv_episodes WHERE indexer NOT IN (1,2)']
                                ])
        self.my_db.action('CREATE INDEX idx_tv_episodes_showid_airdate ON tv_episodes(showid,airdate)')

        self.my_db.action('CREATE INDEX idx_showid ON tv_episodes (showid)')

        self.remove_index('tv_shows', 'idx_indexer_id')
        self.my_db.mass_action([['CREATE TABLE backup_tv_shows (show_id INTEGER PRIMARY KEY, indexer_id NUMERIC, '
                                 'indexer NUMERIC, show_name TEXT, location TEXT, network TEXT, genre TEXT, '
                                 'classification TEXT, runtime NUMERIC, quality NUMERIC, airs TEXT, status TEXT, '
                                 'flatten_folders NUMERIC, paused NUMERIC, startyear NUMERIC, air_by_date NUMERIC, '
                                 'lang TEXT, subtitles NUMERIC, notify_list TEXT, imdb_id TEXT, '
                                 'last_update_indexer NUMERIC, dvdorder NUMERIC, archive_firstmatch NUMERIC, '
                                 'rls_require_words TEXT, rls_ignore_words TEXT, sports NUMERIC, anime NUMERIC, '
                                 'scene NUMERIC, overview TEXT, tag TEXT)'],
                                ['REPLACE INTO backup_tv_shows (show_id, indexer_id, indexer, show_name, location, '
                                 'network, genre, classification, runtime, quality, airs, status, flatten_folders, '
                                 'paused, startyear, air_by_date, lang, subtitles, notify_list, imdb_id, '
                                 'last_update_indexer, dvdorder, archive_firstmatch, rls_require_words, '
                                 'rls_ignore_words, sports, anime, scene, overview, tag) SELECT show_id, indexer_id, '
                                 'indexer, show_name, location, network, genre, classification, runtime, quality, '
                                 'airs, status, flatten_folders, paused, startyear, air_by_date, lang, subtitles, '
                                 'notify_list, imdb_id, last_update_indexer, dvdorder, archive_firstmatch, '
                                 'rls_require_words, rls_ignore_words, sports, anime, scene, overview, tag '
                                 'FROM tv_shows WHERE indexer NOT IN (1,2)'],
                                ['DELETE FROM tv_shows WHERE indexer NOT IN (1,2)']
                                ])
        self.my_db.action('CREATE UNIQUE INDEX idx_indexer_id ON tv_shows (indexer_id)')

        self.remove_index('imdb_info', 'idx_id_indexer_imdb_info')

        self.my_db.mass_action([['ALTER TABLE imdb_info RENAME TO backup_imdb_info'],
                                ['CREATE TABLE imdb_info (indexer_id INTEGER PRIMARY KEY, imdb_id TEXT, '
                                 'title TEXT, year NUMERIC, akas TEXT, runtimes NUMERIC, genres TEXT, '
                                 'countries TEXT, country_codes TEXT, certificates TEXT, rating TEXT, '
                                 'votes INTEGER, last_update NUMERIC)'],
                                ['REPLACE INTO imdb_info (indexer_id, imdb_id, title, year, akas, runtimes, genres, '
                                 'countries, country_codes, certificates, rating, votes, last_update) '
                                 'SELECT indexer_id, imdb_id, title, year, akas, runtimes, genres, '
                                 'countries, country_codes, certificates, rating, votes, last_update '
                                 'FROM backup_imdb_info WHERE indexer IN (1,2)'],
                                ['DELETE FROM backup_imdb_info WHERE indexer IN (1,2)']])

        self.remove_index('blacklist', 'idx_id_indexer_blacklist')

        self.my_db.mass_action([['ALTER TABLE blacklist RENAME TO backup_blacklist'],
                                ['CREATE TABLE blacklist (show_id INTEGER, range TEXT, keyword TEXT)'],
                                ['REPLACE INTO blacklist (show_id, range, keyword) '
                                 'SELECT show_id, range, keyword FROM backup_blacklist '
                                 'WHERE indexer IN (1,2)'],
                                ['DELETE FROM backup_blacklist WHERE indexer IN (1,2)']
                                ])

        self.remove_index('whitelist', 'idx_id_indexer_whitelist')

        self.my_db.mass_action([['ALTER TABLE whitelist RENAME TO backup_whitelist'],
                                ['CREATE TABLE whitelist (show_id INTEGER, range TEXT, keyword TEXT)'],
                                ['REPLACE INTO whitelist (show_id, range, keyword) '
                                 'SELECT show_id, range, keyword FROM backup_whitelist '
                                 'WHERE indexer IN (1,2)'],
                                ['DELETE FROM backup_whitelist WHERE indexer IN (1,2)']
                                ])

        self.remove_index('scene_exceptions', 'idx_id_indexer_scene_exceptions')

        self.my_db.mass_action([['ALTER TABLE scene_exceptions RENAME TO backup_scene_exceptions'],
                                ['CREATE TABLE scene_exceptions (exception_id INTEGER PRIMARY KEY, '
                                 'indexer_id INTEGER KEY, show_name TEXT, season NUMERIC, custom NUMERIC)'],
                                ['REPLACE INTO scene_exceptions (exception_id , indexer_id, show_name, season, '
                                 'custom) SELECT exception_id , indexer_id, show_name, season, '
                                 'custom FROM backup_scene_exceptions WHERE indexer IN (1,2)'],
                                ['DELETE FROM backup_scene_exceptions WHERE indexer IN (1,2)']
                                ])

        self.my_db.mass_action([['ALTER TABLE scene_numbering RENAME TO tmp_scene_numbering'],
                                ['CREATE TABLE scene_numbering (indexer TEXT, indexer_id INTEGER, season INTEGER, '
                                 'episode INTEGER, scene_season INTEGER, scene_episode INTEGER, '
                                 'absolute_number NUMERIC, scene_absolute_number NUMERIC, '
                                 'PRIMARY KEY (indexer_id,season,episode))'],
                                ['REPLACE INTO scene_numbering (indexer, indexer_id, season, episode, '
                                 'scene_season, scene_episode, absolute_number, scene_absolute_number) '
                                 'SELECT indexer, indexer_id, season, episode, '
                                 'scene_season, scene_episode, absolute_number, scene_absolute_number '
                                 'FROM tmp_scene_numbering'],
                                ['DROP TABLE tmp_scene_numbering']
                                ])

        self.remove_index('history', 'idx_id_indexer_history')

        self.my_db.mass_action([['ALTER TABLE history RENAME TO backup_history'],
                                ['CREATE TABLE history (action NUMERIC, date NUMERIC, showid NUMERIC, season NUMERIC, '
                                 'episode NUMERIC, quality NUMERIC, resource TEXT, provider TEXT, version NUMERIC)'],
                                ['REPLACE INTO history (action, date, showid, season, episode, quality, '
                                 'resource, provider, version) SELECT action, date, showid, season, episode, quality, '
                                 'resource, provider, version FROM backup_history WHERE indexer IN (0,1,2)'],
                                ['DELETE FROM backup_history WHERE indexer IN (0,1,2)']
                                ])

        self.set_db_version(20008)

    # regular db rollbacks
    def rollback_20009(self):
        self.remove_table('tv_episodes_watched')

        self.set_db_version(20008)

    def rollback_20008(self):
        self.remove_table('webdl_types')

        self.set_db_version(20007)

    def rollback_20007(self):
        # watched_state moved to 20009 and this now a version rollback
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
