def get_te_data():
    """
    Gets the TE data from the full nfl roster
    :return: df, the TE data.
    """
    df = pd.read_csv('team_rosters.csv')
    te_data = df[df['Pos.'] == 'TE']
    print(te_data)
    return te_data

def get_position_data(position):
    """
    Gets the TE data from the full nfl roster
    :return: df, the TE data.
    """
    df = pd.read_csv('team_rosters.csv')
    pos_data = df[df['Pos.'] == position]
    print(pos_data)
    return pos_data


wr_data = get_position_data('TE')
