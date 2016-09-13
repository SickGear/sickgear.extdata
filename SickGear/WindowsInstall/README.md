# SickGear.WindowsInstall

Purpose: Installs SickGear on Windows

This install will download and use official Git and Python distributions, you must
manually install SickGear if you prefer to use your own pre-installed versions.

#### Features of SickGear.WindowsInstall

* Before install, the user can change the port used to display Sickgear in the browser
* Download SickGear dependencies (Git, Python, Cheetah)
* Install SickGear in a self-contained directory with appropriate 32-bit or 64-bit dependencies
* Create Start Menu shortcuts
* When uninstalling, ask user if they want to delete or preserve database and configuration files
* (REMOVE THIS SHIT) Install SickGear as a Windows service (handled by NSSM)

#### Download

See the [releases](https://github.com/SickGear/sickgear.extdata/SickGear/WindowsInstall/releases) tab

#### How It Works

The install fetches a 'seed' file, located [here](https://raw.githubusercontent.com/SickGear/sickgear.extdata/SickGear/WindowsInstall/deps.ini)

The seed file is used to ..
1) ensure that the latest install version is being used
2) lists dependencies, each with; download location, file size and SHA1 verification hash

After the install wizard steps are complete, dependencies are downloaded, verified, and installed
into the directory chosen by the user. Git is used to install a clone of the SickGear repository.

The original open source installer was adapted to SickGear, credit and thanks to the original install author: VinceVal
The installer system uses the [Inno Setup](http://www.jrsoftware.org/isinfo.php) by Jordan Russell
