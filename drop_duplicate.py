def del_duplicate(df):
	"""
	del_duplicate - drop duplicates in columns in dataframe and
	updates dataframe
	df - Dataframe
	return nothing
	"""
	df.drop_duplicates().reset_index(drop=True, inplace=True)