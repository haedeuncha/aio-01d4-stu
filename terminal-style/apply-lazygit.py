from pathlib import Path
import datetime, shutil, yaml

path = Path.home() / '.config/lazygit/config.yml'
path.parent.mkdir(parents=True, exist_ok=True)
if path.exists():
    backup = path.with_name('config.yml.backup-' + datetime.datetime.now().strftime('%Y%m%d-%H%M%S'))
    shutil.copy2(path, backup)
    print('Backup:', backup)
    config = yaml.safe_load(path.read_text()) or {}
else:
    config = {}
    print('No previous config; created new theme config.')
gui = config.setdefault('gui', {})
gui.update(sidePanelWidth=0.40, border='rounded', commandLogSize=3, showRandomTip=False)
gui.setdefault('theme', {}).update({
    'activeBorderColor': ['#9670B0', 'bold'],
    'inactiveBorderColor': ['#C6AFBF'],
    'searchingActiveBorderColor': ['#AD4968', 'bold'],
    'optionsTextColor': ['#586FA3'],
    'selectedLineBgColor': ['#F3D8E5'],
    'inactiveViewSelectedLineBgColor': ['#F4E9EF'],
    'cherryPickedCommitFgColor': ['#586FA3'],
    'cherryPickedCommitBgColor': ['#E5E6F5'],
    'markedBaseCommitFgColor': ['#8762A4'],
    'markedBaseCommitBgColor': ['#F5E8C9'],
    'unstagedChangesColor': ['#AD4968'],
    'defaultFgColor': ['#51434E'],
})
text = yaml.safe_dump(config, allow_unicode=True, sort_keys=False)
assert yaml.safe_load(text)['gui']['sidePanelWidth'] == 0.40
path.write_text(text)
print('Lazygit theme applied:', path)
