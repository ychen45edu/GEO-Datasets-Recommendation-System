import pandas as pd

# Dictionary for GSEID : Contact Author
def g_c_dic(csv):
    """
    Generate a mapping dictionary of series accession IDs to contact author names.

    Parameters:
    ----------
    csv : str
        File path to the CSV containing series metadata with 'Accession' and 'Contact' columns.

    Returns:
    -------
    dict
        Dictionary mapping each series accession ID (GSEID) to its corresponding contact author name.
    """
    df=pd.read_csv(csv, dtype=str)
    gseid_contact_dict = dict(zip(df.Accession, df.Contact))
    return  gseid_contact_dict


# Create dictionary for gseid : pmid
def series_ls_w_contact(csv,filter=0):
    """
    Create a mapping dictionary of series accession IDs (GSEID) to their associated PubMed IDs (PMID).

    Workflow:
    1. Reads the CSV metadata as string data and replaces missing values with empty strings.
    2. Optional filtering (`filter=1`): Restricts records to contacts associated with more than 8 entries.
    3. Maps 'Accession' to 'PubMed ID'.
    4. Splits multi-value PMIDs delimited by semicolons into lists.
    5. Cleans float-style string formatting artifacts (e.g., '.0') from PubMed ID strings.

    Parameters:
    ----------
    csv : str
        File path to the CSV containing metadata (must include 'Accession', 'PubMed ID', and 'Contact').
    filter : int, optional (default=0)
        Filter flag. If set to 1, filters data to include only contacts with a count greater than 8.

    Returns:
    -------
    dict
        Dictionary mapping series accession IDs to either a single PubMed ID string,
        a list of PubMed ID strings, or an empty string if no PMID is present.
    """
    df=pd.read_csv(csv, dtype=str)
    df = df.fillna('')

    if filter ==1:
        df = df.dropna(subset=["PubMed ID"])
        df2=df.copy()
        df=df.groupby('Contact').size().reset_index(name='Count')
        rslt_df = df[df['Count'] > 8]
        rslt_ls=rslt_df["Contact"].tolist()
        t_f = df2['Contact'].isin(rslt_ls)
        df2=df2[t_f]
    else:
        df2 = df.copy()

    df2.rename(columns={'PubMed ID': 'PubMed_ID'}, inplace=True)
    gse_pmid_dict = dict(zip(df2.Accession, df2.PubMed_ID))

    # Split PMID into list for those GSEIDs with more than one PMID
    for i in gse_pmid_dict:
        if ";" in str(gse_pmid_dict[i]):
            gse_pmid_dict[i]=gse_pmid_dict[i].split(";")

    for k, v in gse_pmid_dict.items():
        if "." in str(v):
            gse_pmid_dict[k] = v.replace(".0", "")
    return gse_pmid_dict