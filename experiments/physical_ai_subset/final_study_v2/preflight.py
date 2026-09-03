from pathlib import Path
import csv,json
ROOT=Path(__file__).resolve().parent
def main():
 p=json.loads((ROOT/'protocol.json').read_text()); rows=list(csv.DictReader((ROOT/'candidate_matrix.csv').open()))
 assert len(p['scenarios'])==5 and len(p['models'])==3 and p['runs']==[1,2] and p['total_calls']==30
 assert len(rows)==30 and len({r['candidate_id'] for r in rows})==30
 assert not any((ROOT/'raw').glob('*')) if (ROOT/'raw').exists() else True
 print('V2 PREFLIGHT PASS: 5 scenarios, 3 models, 2 runs, 30 cells, zero outputs')
if __name__=='__main__': main()
