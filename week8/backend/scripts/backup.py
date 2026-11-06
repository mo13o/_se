import argparse,shutil
from datetime import datetime
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument("database",type=Path);p.add_argument("--output",type=Path,default=Path("backups"));a=p.parse_args();a.output.mkdir(parents=True,exist_ok=True);target=a.output/f"taskflow-{datetime.now():%Y%m%d-%H%M%S}.db";shutil.copy2(a.database,target);print(target.resolve())
