from nbclient import NotebookClient
import nbformat
from pathlib import Path

nb_path = Path(__file__).resolve().parent.parent / 'notebooks' / 'session_20251231_analysis.ipynb'
nb = nbformat.read(nb_path, as_version=4)
client = NotebookClient(nb, timeout=600, kernel_name='python3')
print('Executing notebook:', nb_path)
client.execute()
out_path = nb_path.parent / 'session_20251231_analysis_executed.ipynb'
nbformat.write(nb, out_path)
print('Saved executed notebook to', out_path)
