def drop_columns(df, col):
	"""
	drop_columns - function to drop columns in dataframe and update dataframe
	col - Column names in dataframe
	df - Dataframe
	return nothing
	"""
	for i in col:
		df.drop(columns=i, inplace=True)