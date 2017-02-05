#include <.\idp\idp.iss>

#define SickGearInstallerVersion "v0.1"

#define AppId "{5BF08F1D-DD06-4DCD-B454-4218E589EDCC}"
#define AppName "SickGear"
#define AppVersion "master"
#define AppPublisher "SickGear"
#define AppURL "https://github.com/SickGear/SickGear/"
;#define AppServiceName AppName
;#define AppServiceDescription "Automatic Video Library Manager for TV Shows"
;#define ServiceStartIcon "{group}\Start " + AppName + " Service"
;#define ServiceStopIcon "{group}\Stop " + AppName + " Service"

#define DefaultPort 8082

#define InstallerVersion 20003
#define InstallerSeedUrl "https://raw.githubusercontent.com/SickGear/sickgear.extdata/SickGear/WindowsInstall/deps.ini"
#define AppRepoUrl "https://github.com/SickGear/SickGear.git"

[Setup]
AppId={#AppId}
AppName={#AppName}
AppVersion={#AppVersion}
AppVerName={#AppName} ({#AppVersion})
AppPublisher={#AppPublisher}
AppPublisherURL={#AppURL}
AppSupportURL={#AppURL}
AppUpdatesURL={#AppURL}
DefaultDirName={sd}\{#AppName}
DefaultGroupName={#AppName}
AllowNoIcons=yes
ArchitecturesInstallIn64BitMode=x64
OutputBaseFilename={#AppName}Installer
SolidCompression=yes
UninstallDisplayIcon={app}\Installer\SickGear.ico
UninstallFilesDir={app}\Installer
ExtraDiskSpaceRequired=524288000
SetupIconFile=assets\SickGear.ico
WizardImageFile=assets\Wizard.bmp
WizardSmallImageFile=assets\WizardSmall.bmp

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked

[Files]
Source: "utils\unzip.exe"; Flags: dontcopy
Source: "utils\tar.exe"; Flags: dontcopy
Source: "utils\gzip.exe"; Flags: dontcopy
Source: "assets\SickGear.ico"; DestDir: "{app}\Installer"
Source: "assets\github.ico"; DestDir: "{app}\Installer"

[Dirs]
Name: "{app}\Data"

[Icons]
Name: "{group}\{#AppName}"; Filename: "http://localhost:{code:GetWebPort}/"; IconFilename: "{app}\Installer\SickGear.ico"
Name: "{commondesktop}\{#AppName}"; Filename: "http://localhost:{code:GetWebPort}/"; IconFilename: "{app}\Installer\SickGear.ico"; Tasks: desktopicon
Name: "{group}\{cm:ProgramOnTheWeb,{#AppName}}"; Filename: "{#AppURL}"; IconFilename: "{app}\Installer\SickGear.ico"; Flags: excludefromshowinnewinstall
Name: "{group}\{#AppName} on GitHub"; Filename: "{#AppRepoUrl}"; IconFilename: "{app}\Installer\github.ico"; Flags: excludefromshowinnewinstall

[Run]
;SickGear
Filename: "{app}\Git\cmd\git.exe"; Parameters: "clone {#AppRepoUrl} {app}\{#AppName}"; StatusMsg: "Installing {#AppName}..."
;Filename: "xcopy.exe"; Parameters: """C:\SickGearInstaller\SickGear"" ""{app}\{#AppName}"" /E /I /H /Y"; Flags: runminimized; StatusMsg: "Installing {#AppName}..."
;Open
Filename: "http://localhost:{code:GetWebPort}/"; Flags: postinstall shellexec; Description: "Open {#AppName} in browser"

[UninstallRun]

[UninstallDelete]
Type: filesandordirs; Name: "{app}\Python"
Type: filesandordirs; Name: "{app}\Git"
Type: filesandordirs; Name: "{app}\{#AppName}"
Type: dirifempty; Name: "{app}"

[Messages]
WelcomeLabel2=This will install [name/ver] on your computer.%n%nAn internet connection is needed to download required packages.%n%nThis install will download and use official Git and Python distributions, you must manually install [name] if you prefer to use your own pre-installed versions.
AboutSetupNote=SickGear.WindowsInstall {#SickGearInstallerVersion}
BeveledLabel=SickGear.WindowsInstall {#SickGearInstallerVersion}

[Code]
type
  TDependency = record
    Name:     String;
    URL:      String;
    Filename: String;
    Size:     Integer;
    SHA1:     String;
  end;

  IShellLinkW = interface(IUnknown)
    '{000214F9-0000-0000-C000-000000000046}'
    procedure Dummy;
    procedure Dummy2;
    procedure Dummy3;
    function GetDescription(pszName: String; cchMaxName: Integer): HResult;
    function SetDescription(pszName: String): HResult;
    function GetWorkingDirectory(pszDir: String; cchMaxPath: Integer): HResult;
    function SetWorkingDirectory(pszDir: String): HResult;
    function GetArguments(pszArgs: String; cchMaxPath: Integer): HResult;
    function SetArguments(pszArgs: String): HResult;
    function GetHotkey(var pwHotkey: Word): HResult;
    function SetHotkey(wHotkey: Word): HResult;
    function GetShowCmd(out piShowCmd: Integer): HResult;
    function SetShowCmd(iShowCmd: Integer): HResult;
    function GetIconLocation(pszIconPath: String; cchIconPath: Integer;
      out piIcon: Integer): HResult;
    function SetIconLocation(pszIconPath: String; iIcon: Integer): HResult;
    function SetRelativePath(pszPathRel: String; dwReserved: DWORD): HResult;
    function Resolve(Wnd: HWND; fFlags: DWORD): HResult;
    function SetPath(pszFile: String): HResult;
  end;

  IPersist = interface(IUnknown)
    '{0000010C-0000-0000-C000-000000000046}'
    function GetClassID(var classID: TGUID): HResult;
  end;

  IPersistFile = interface(IPersist)
    '{0000010B-0000-0000-C000-000000000046}'
    function IsDirty: HResult;
    function Load(pszFileName: String; dwMode: Longint): HResult;
    function Save(pszFileName: String; fRemember: BOOL): HResult;
    function SaveCompleted(pszFileName: String): HResult;
    function GetCurFile(out pszFileName: String): HResult;
  end;

  IShellLinkDataList = interface(IUnknown)
    '{45E2B4AE-B1C3-11D0-B92F-00A0C90312E1}'
    procedure Dummy;
    procedure Dummy2;
    procedure Dummy3;
    function GetFlags(out dwFlags: DWORD): HResult;
    function SetFlags(dwFlags: DWORD): HResult;
  end;

const
  MinPort = 1;
  MaxPort = 65535;
  WM_CLOSE             = $0010;
  GENERIC_WRITE        = $40000000;
  GENERIC_READ         = $80000000;
  OPEN_EXISTING        = 3;
  INVALID_HANDLE_VALUE = $FFFFFFFF;
  SLDF_RUNAS_USER      = $00002000;
  CLSID_ShellLink = '{00021401-0000-0000-C000-000000000046}';

var
  // This lets AbortInstallation() terminate setup without prompting the user
  CancelWithoutPrompt: Boolean;
  ErrorMessage, LocalFilesDir: String;
  SeedDownloadPageId, DependencyDownloadPageId: Integer;
  PythonDep, CheetahDep, GitDep: TDependency;
  InstallDepPage: TOutputProgressWizardPage;
  OptionsPage: TInputQueryWizardPage;
  // Uninstall variables
  UninstallRemoveData: Boolean;

// Import some Win32 functions
function CreateFile(
  lpFileName: String;
  dwDesiredAccess: LongWord;
  dwSharedMode: LongWord;
  lpSecurityAttributes: LongWord;
  dwCreationDisposition: LongWord;
  dwFlagsAndAttributes: LongWord;
  hTemplateFile: LongWord): LongWord;
external 'CreateFileW@kernel32.dll stdcall';

function CloseHandle(hObject: LongWord): Boolean;
external 'CloseHandle@kernel32.dll stdcall';

procedure AbortInstallation(ErrorMessage: String);
begin
  MsgBox(ErrorMessage + #13#10#13#10 'Setup will now terminate.', mbError, 0)
  CancelWithoutPrompt := True
  PostMessage(WizardForm.Handle, WM_CLOSE, 0, 0);
end;

procedure CheckInstallerVersion(SeedFile: String);
var
  InstallerVersion, CurrentVersion: Integer;
  DownloadUrl: String;
begin
  InstallerVersion := StrToInt(ExpandConstant('{#InstallerVersion}'))

  CurrentVersion := GetIniInt('Installer', 'Version', 0, 0, MaxInt, SeedFile)

  if CurrentVersion = 0 then begin
    AbortInstallation('Unable to parse configuration.')
  end;

  if CurrentVersion > InstallerVersion then begin
    DownloadUrl := GetIniString('Installer', 'DownloadUrl', ExpandConstant('{#AppURL}'), SeedFile)
    AbortInstallation(ExpandConstant('This is an old version of the {#AppName} installer. Please get the latest version at:') + #13#10#13#10 + DownloadUrl)
  end;
end;

procedure ParseDependency(var Dependency: TDependency; Name, SeedFile: String);
var
  LocalFile: String;
begin
  Dependency.Name     := Name;
  Dependency.URL      := GetIniString(Name, 'url', '', SeedFile)
  Dependency.Filename := Dependency.URL
  Dependency.Size     := GetIniInt(Name, 'size', 0, 0, MaxInt, SeedFile)
  Dependency.SHA1     := GetIniString(Name, 'sha1', '', SeedFile)

  if (Dependency.URL = '') or (Dependency.Size = 0) or (Dependency.SHA1 = '') then begin
    AbortInstallation('Error parsing dependency information for ' + Name + '.')
  end;

  while Pos('/', Dependency.Filename) <> 0 do begin
    Delete(Dependency.Filename, 1, Pos('/', Dependency.Filename))
  end;

  if LocalFilesDir <> '' then begin
    LocalFile := LocalFilesDir + '\' + Dependency.Filename
  end;
  if (LocalFile <> '') and (FileExists(LocalFile)) then begin
    FileCopy(LocalFile, ExpandConstant('{tmp}\') + Dependency.Filename, True)
  end else begin
    idpAddFileSize(Dependency.URL, ExpandConstant('{tmp}\') + Dependency.Filename, Dependency.Size)
  end
end;

procedure ParseSeedFile();
var
  SeedFile: String;
  Arch: String;
  DownloadPage: TWizardPage;
begin
  SeedFile := ExpandConstant('{tmp}\installer.ini')

  // Make sure we're running the latest version of the installer
  CheckInstallerVersion(SeedFile)

  if Is64BitInstallMode then
    Arch := 'x64'
  else
    Arch := 'x86';

  ParseDependency(PythonDep,    'Python.'    + Arch, SeedFile)
  ParseDependency(CheetahDep,   'Cheetah',           SeedFile)
  ParseDependency(GitDep,       'Git.'       + Arch, SeedFile)

  DependencyDownloadPageId := idpCreateDownloadForm(wpPreparing)
  DownloadPage := PageFromID(DependencyDownloadPageId)
  DownloadPage.Caption := 'Downloading Dependencies'
  DownloadPage.Description := ExpandConstant('Setup is downloading {#AppName} dependencies...')

  idpSetOption('DetailedMode', '1')
  idpSetOption('DetailsButton', '0')

  idpConnectControls()
end;

procedure InitializeSeedDownload();
var
  DownloadPage: TWizardPage;
  Seed: String;
  IsRemote: Boolean;
begin
  IsRemote := True

  Seed := ExpandConstant('{param:SEED}')
  if (Lowercase(Copy(Seed, 1, 7)) <> 'http://') and (Lowercase(Copy(Seed, 1, 8)) <> 'https://') then begin
    if Seed = '' then begin
      Seed := ExpandConstant('{#InstallerSeedUrl}')
    end else begin
      if FileExists(Seed) then begin
        IsRemote := False
      end else begin
        MsgBox('Invalid SEED specified: ' + Seed, mbError, 0)
        Seed := ExpandConstant('{#InstallerSeedUrl}')
      end;
    end;
  end;

  if not IsRemote then begin
    FileCopy(Seed, ExpandConstant('{tmp}\installer.ini'), False)
    ParseSeedFile()
  end else begin
    // Download the installer seed INI file
    // add a dummy size here otherwise the installer crashes (divide by 0)
    // when runnning in silent mode, a bug in IDP maybe?
    idpAddFileSize(Seed, ExpandConstant('{tmp}\installer.ini'), 1024)

    SeedDownloadPageId := idpCreateDownloadForm(wpWelcome)
    DownloadPage := PageFromID(SeedDownloadPageId)
    DownloadPage.Caption := 'Downloading Installer Configuration'
    DownloadPage.Description := 'Setup is downloading it''s configuration file...'

    idpConnectControls()
  end;
end;

function CheckFileInUse(Filename: String): Boolean;
var
  FileHandle: LongWord;
begin
  if not FileExists(Filename) then begin
    Result := False
    exit
  end;

  FileHandle := CreateFile(Filename, GENERIC_READ or GENERIC_WRITE, 0, 0, OPEN_EXISTING, 0, 0)
  if (FileHandle <> 0) and (FileHandle <> INVALID_HANDLE_VALUE) then begin
    CloseHandle(FileHandle)
    Result := False
  end else begin
    Result := True
  end;
end;

function GetWebPort(Param: String): String;
begin
  Result := OptionsPage.Values[0]
end;

procedure CleanPython();
var
  PythonPath: String;
begin
  PythonPath := ExpandConstant('{app}\Python')

  DelTree(PythonPath + '\*.msi',        False, True, False)
  DelTree(PythonPath + '\Doc',          True,  True, True)
  DelTree(PythonPath + '\Lib\test\*.*', False, True, True)
  DelTree(PythonPath + '\Scripts',      True,  True, True)
  DelTree(PythonPath + '\tcl',          True,  True, True)
  DelTree(PythonPath + '\Tools',        True,  True, True)
end;

procedure InstallPython();
var
  ResultCode: Integer;
begin
  InstallDepPage.SetText('Installing Python...', '')
  Exec('msiexec.exe', ExpandConstantEx('/A "{tmp}\{filename}" /QN TARGETDIR="{app}\Python"', 'filename', PythonDep.Filename), '', SW_SHOW, ewWaitUntilTerminated, ResultCode)
  CleanPython()
  InstallDepPage.SetProgress(InstallDepPage.ProgressBar.Position+1, InstallDepPage.ProgressBar.Max)
end;

procedure InstallCheetah();
var
  ResultCode: Integer;
  DirName: String;
begin
  InstallDepPage.SetText('Installing Cheetah...', '')
  ExtractTemporaryFile('gzip.exe')
  ExtractTemporaryFile('tar.exe')
  DirName := CheetahDep.Filename
  if (Copy(DirName, Length(DirName)-6, 7) = '.tar.gz') then begin
    Delete(DirName, Length(DirName)-6, 7)
  end;
  DirName := ExpandConstant('{tmp}\') + DirName
  Exec(ExpandConstant('{cmd}'), ExpandConstantEx('/C "cd "{tmp}" && gzip.exe -dc "{filename}" | tar.exe xf -"', 'filename', CheetahDep.Filename), '', SW_HIDE, ewWaitUntilTerminated, ResultCode)
  if DirExists(DirName) then begin
    Exec(ExpandConstant('{app}\Python\python.exe'), 'setup.py install', DirName, SW_HIDE, ewWaitUntilTerminated, ResultCode)
  end else begin
    MsgBox('Error installing Cheetah.', mbError, 0)
  end;
  InstallDepPage.SetProgress(InstallDepPage.ProgressBar.Position+1, InstallDepPage.ProgressBar.Max)
end;

procedure InstallGit();
var
  ResultCode: Integer;
begin
  InstallDepPage.SetText('Installing Git...', '')
  Exec(ExpandConstantEx('{tmp}\{filename}', 'filename', GitDep.Filename), ExpandConstant('-InstallPath="{app}\Git" -y -gm2'), '', SW_SHOW, ewWaitUntilTerminated, ResultCode)
  InstallDepPage.SetProgress(InstallDepPage.ProgressBar.Position+1, InstallDepPage.ProgressBar.Max)
end;

function VerifyDependency(Dependency: TDependency): Boolean;
begin
  Result := True

  InstallDepPage.SetText('Verifying dependency files...', Dependency.Filename)
  if GetSHA1OfFile(ExpandConstant('{tmp}\') + Dependency.Filename) <> Dependency.SHA1 then begin
    MsgBox('SHA1 hash of ' + Dependency.Filename + ' does not match.', mbError, 0)
    Result := False
  end;
  InstallDepPage.SetProgress(InstallDepPage.ProgressBar.Position+1, InstallDepPage.ProgressBar.Max)
end;

function VerifyDependencies(): Boolean;
begin
  Result := True

  Result := Result and VerifyDependency(PythonDep)
  Result := Result and VerifyDependency(CheetahDep)
  Result := Result and VerifyDependency(GitDep)
end;

function PrepareToInstall(var NeedsRestart: Boolean): String;
begin
  if ErrorMessage <> '' then begin
    Result := ErrorMessage
  end;
end;

procedure InstallDependencies();
begin
  try
    InstallDepPage.Show
    InstallDepPage.SetProgress(0, 8)
    if VerifyDependencies() then begin
      InstallPython()
      InstallCheetah()
      InstallGit()
    end else begin
      ErrorMessage := 'There was an error installing the required dependencies.'
    end;
  finally
    InstallDepPage.Hide
  end;
end;

procedure InitializeWizard();
begin
  InitializeSeedDownload()

  idpInitMessages()

  InstallDepPage := CreateOutputProgressPage('Installing Dependencies', ExpandConstant('Setup is installing {#AppName} dependencies...'));

  OptionsPage := CreateInputQueryPage(wpSelectProgramGroup, 'Additional Options', ExpandConstant('Additional {#AppName} configuration options'), '');
  OptionsPage.Add(ExpandConstant('{#AppName} Web Server Port:'), False)
  OptionsPage.Values[0] := ExpandConstant('{#DefaultPort}')
end;

function ShellLinkRunAsAdmin(LinkFilename: String): Boolean;
var
  Obj: IUnknown;
  SL: IShellLinkW;
  PF: IPersistFile;
  DL: IShellLinkDataList;
  Flags: DWORD;
begin
  try
    Obj := CreateComObject(StringToGuid(CLSID_ShellLink));

    SL := IShellLinkW(Obj);
    PF := IPersistFile(Obj);

    // Load the ShellLink
    OleCheck(PF.Load(LinkFilename, 0));

    // Set the SLDF_RUNAS_USER flag
    DL := IShellLinkDataList(Obj);
    OleCheck(DL.GetFlags(Flags))
    OleCheck(DL.SetFlags(Flags or SLDF_RUNAS_USER))

    // Save the ShellLink
    OleCheck(PF.Save(LinkFilename, True));

    Result := True
  except
    Result := False
  end;
end;

function InitializeSetup(): Boolean;
begin
  CancelWithoutPrompt := False

  LocalFilesDir := ExpandConstant('{param:LOCALFILES}')
  if (LocalFilesDir <> '') and (not DirExists(LocalFilesDir)) then begin
    MsgBox('Invalid LOCALFILES specified: ' + LocalFilesDir, mbError, 0)
    LocalFilesDir := ''
  end;

  // Don't allow installations over top
  if RegKeyExists(HKEY_LOCAL_MACHINE, ExpandConstant('Software\Microsoft\Windows\CurrentVersion\Uninstall\{#AppId}_is1')) then begin
    MsgBox(ExpandConstant('{#AppName} is already installed. If you''re reinstalling or upgrading, please uninstall the current version first.'), mbError, 0)
    Result := False
  end else begin
    Result := True
  end;
end;

function NextButtonClick(CurPageID: Integer): Boolean;
var
  Port: Integer;
begin
  Result := True

  if CurPageID = SeedDownloadPageId then begin
    ParseSeedFile()
  end else if CurPageId = OptionsPage.ID then begin
    // Make sure valid port is specified
    Port := StrToIntDef(OptionsPage.Values[0], 0)
    if (Port = 0) or (Port < MinPort) or (Port > MaxPort) then begin
      MsgBox(FmtMessage('Please specify a valid port between %1 and %2.', [IntToStr(MinPort), IntToStr(MaxPort)]), mbError, 0)
      Result := False;
    end;
  end;
end;

function UninstallShouldRemoveData(): Boolean;
begin
  Result := MsgBox(ExpandConstant('Do you want to remove your {#AppName} database and configuration?' #13#10#13#10 'Select No if you plan on reinstalling {#AppName}.'), mbConfirmation, MB_YESNO or MB_DEFBUTTON2) = IDYES;
end;

procedure CancelButtonClick(CurPageID: Integer; var Cancel, Confirm: Boolean);
begin
  Confirm := not CancelWithoutPrompt;
end;

procedure InitializeUninstallProgressForm();
begin
  UninstallRemoveData := UninstallShouldRemoveData()
end;

procedure CurUninstallStepChanged(CurUninstallStep: TUninstallStep);
begin
  if CurUninstallStep = usUninstall then begin
    // Stop service
    //StopService()

    // Remove data if requested
    if UninstallRemoveData then begin
      DelTree(ExpandConstant('{app}\Data'), True, True, True)
    end;
  end;
end;

function UpdateReadyMemo(Space, NewLine, MemoUserInfoInfo, MemoDirInfo,
  MemoTypeInfo, MemoComponentsInfo, MemoGroupInfo, MemoTasksInfo: String): String;
begin
  Result := MemoDirInfo + NewLine + NewLine + \
            MemoGroupInfo + NewLine + NewLine + \
            'Download and install dependencies:' + NewLine + \
            Space + 'Git' + NewLine + \
            Space + 'Python' + NewLine + \
            Space + 'Cheetah' + NewLine + NewLine + \
            'Web server port:' + NewLine + Space + GetWebPort('')

  if MemoTasksInfo <> '' then begin
    Result := Result + NewLine + NewLine + MemoTasksInfo
  end;
end;

procedure CurStepChanged(CurStep: TSetupStep);
begin
  if CurStep = ssInstall then begin
    InstallDependencies()
  end;
end;
