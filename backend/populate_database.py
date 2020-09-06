import os
import pickle
import psycopg2

# File paths
features_pickle_filename = 'features_coco_segment.pickle'
imagenames_pickle_filename = 'imagenames_coco_segment.pickle'
sql_script = 'database.psql'

# Database access env variables
DBUSER = os.environ['POSTGRES_USER']
DBPASS = os.environ['POSTGRES_PASSWORD']
DBNAME = os.environ['POSTGRES_DB']
DBPORT = '5432'

def get_connection():
	conn = psycopg2.connect(database=DBNAME, user=DBUSER, password=DBPASS, port=DBPORT)
	return conn

def add_feature(conn, name, feature):
	try:
		cur = conn.cursor()
		cur.execute(f'INSERT INTO image (name, feture_vector) values ({name}, {feature});')
		result = cur.fetchone()
		conn.commit()
		cur.close()
	except (Exception, psycopg2.DatabaseError) as error:
		print(error)

def drop_tables(conn):
	try:
		cur = conn.cursor()
		cur.execute('DROP TABLE image;')
		result = cur.fetchone()
		conn.commit()
		cur.close()
	except (Exception, psycopg2.DatabaseError) as error:
		print(error)

def create_table(conn):
	try:
		cur = conn.cursor()
		sql_file = open('file.sql','r')
		cur.execute(sql_file.read())
		result = cur.fetchone()
		conn.commit()
		cur.close()
	except (Exception, psycopg2.DatabaseError) as error:
		print(error)

if __name__ == '__main__':
	conn = get_connection()

	drop_table(conn)
	create_table(conn)
	m
	feature_list = pickle.load(open(features_pickle_filename, 'rb'))
	names = pickle.load(open(imagenames_pickle_filename, 'rb'))

	add_feature(conn, name[0], feature_list[0])

	for i, name in enumerate(names):
		add_feature(conn, name, feature_list[i])
