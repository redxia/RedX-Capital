import logging

#################################

log = logging.getLogger(__name__)

#################################

def format_cursor(cur, n=10) -> str:
    '''
    Calls fetchmany(n), and uses pandas to format as a table
    '''

    # Nothing to do?
    if not cur: return

    # Get column names
    columns = [col[0] for col in cur.description]

    # Get first n rows
    data = cur.fetchmany(n)

    # Print
    if len(data)>0:
        import pandas as pd
        pd.set_option('display.width', None)
        df = pd.DataFrame(data=data, columns=columns)
        if len(data)==1: df = df.transpose()
        return str(df)

#################################

def format_rows(rows, cols=None) -> str:

    # Empty or Null
    if not rows:
        return f'-- RESULT {rows}'

    # Single value
    if len(rows)==1 and len(rows[0])==1:
       return f'-- {rows[0][0]}'
    
    n = len(rows)
    if n > 5000: 
        log.warning(f'TRUNCATING OUTPUT FROM {n} to 1000 ROWS')
        rows = rows[:1000]
    # # Row of values
    # if len(rows)==1 and len(rows[0])>1:
    #     return '\n'.join([f'-- {value}' for value in rows[0]]) 

    max_width = lambda i: max(len(cols[i][0]), len(str(max(rows, key=lambda r: len(str(r[i])))[i]))) # Sorry

    one_line = lambda x: 'NULL' if x==None else str(x).replace('\r','').replace('\n',' ').replace('\t',' ')[:200]

    padded = lambda i,c: c + (' ' * (max_width(i) - len(c or '')))

    # Table 
    s  = '-- ' + (' | '.join([padded(i,c[0]) for i,c in enumerate(cols)]) +'\n') if cols else ''
    s += '-- ' + (' | '.join(['-'*len(padded(i,c[0])) for i,c in enumerate(cols)]) +'\n') if cols else ''
    for row in rows:
        # s += '-- ' + (' | '.join([padded(i,str(c)) for i,c in enumerate(row)]) +'\n')
        s += '-- ' + (' | '.join([padded(i,one_line(c)) for i,c in enumerate(row)]) +'\n')
    return (s)

#################################

