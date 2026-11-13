; Inno Setup Script for Algoo IDE
#ifndef AppVersion
  #define AppVersion "1.0.0"
#endif

[Setup]
AppId={{8F3B5C1E-9E2A-4D1C-9B7A-4F62D2E1A109}
AppName=Algoo
AppVersion={#AppVersion}
AppPublisher=softsurgery
AppPublisherURL=https://github.com/softsurgery/algoo
AppSupportURL=https://github.com/softsurgery/algoo/issues
AppUpdatesURL=https://github.com/softsurgery/algoo/releases
DefaultDirName={autopf}\Algoo
DefaultGroupName=Algoo
AllowNoIcons=yes
OutputDir=..\..\dist
OutputBaseFilename=Algoo-Setup-{#AppVersion}
Compression=lzma2
SolidCompression=yes
WizardStyle=modern
ChangesAssociations=yes

[Languages]
Name: "french"; MessagesFile: "compiler:Languages\French.isl"
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked
Name: "associatealgo"; Description: "Associer les fichiers .algo avec Algoo"; GroupDescription: "Associations de fichiers :"

[Files]
Source: "..\..\dist\Algoo\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{group}\Algoo"; Filename: "{app}\Algoo.exe"
Name: "{group}\{cm:UninstallProgram,Algoo}"; Filename: "{uninstallexe}"
Name: "{autodesktop}\Algoo"; Filename: "{app}\Algoo.exe"; Tasks: desktopicon

[Registry]
Root: HKCR; Subkey: ".algo"; ValueType: string; ValueName: ""; ValueData: "Algoo.AlgoFile"; Flags: uninsdeletevalue; Tasks: associatealgo
Root: HKCR; Subkey: "Algoo.AlgoFile"; ValueType: string; ValueName: ""; ValueData: "Fichier Algorithme Algoo"; Flags: uninsdeletekey; Tasks: associatealgo
Root: HKCR; Subkey: "Algoo.AlgoFile\DefaultIcon"; ValueType: string; ValueName: ""; ValueData: "{app}\Algoo.exe,0"; Tasks: associatealgo
Root: HKCR; Subkey: "Algoo.AlgoFile\shell\open\command"; ValueType: string; ValueName: ""; ValueData: """{app}\Algoo.exe"" ""%1"""; Tasks: associatealgo

[Run]
Filename: "{app}\Algoo.exe"; Description: "{cm:LaunchProgram,Algoo}"; Flags: nowait postinstall skipifsilent
