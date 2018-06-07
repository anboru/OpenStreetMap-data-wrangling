
# coding: utf-8

# In[2]:

import sqlite3
import pprint
db = sqlite3.connect("C:\Users\Anna\sqlite-windows\sqlite_windows\Project3.db")
c = db.cursor()


# In[3]:

# Compute number of unique users
query = '''
select count (distinct uid)
from (select uid from ways UNION ALL select uid from nodes)
'''
c.execute(query)
rows = c.fetchall()
pprint.pprint(rows)


# In[4]:

# Compute number of ways and nodes
query = '''
select 'Number of ways', count (distinct id)
from ways
UNION all
select 'Number of nodes', count (distinct id)
from nodes;
'''
c.execute(query)
rows = c.fetchall()
pprint.pprint(rows)


# In[5]:

# Compute number of top ten most used types of tags and number of distinct keys per type
query = '''
select type, count(type), count(distinct key)
from (select type, key from ways_tags UNION ALL select type, key from nodes_tags)
group by type
order by count(type) desc
limit 10
'''
c.execute(query)
rows = c.fetchall()
pprint.pprint(rows)

# Compute number of top 5 most used keys of type "regular"
query = '''
select key, count(*)
from (select key from ways_tags where type = 'regular' 
UNION ALL select key from nodes_tags where type = 'regular')
group by key
order by count(*) desc
limit 5
'''
c.execute(query)
rows = c.fetchall()
pprint.pprint(rows)


# In[6]:

#Compute number of amenities related to cuisine
query = '''
select value, count(*)
from nodes_tags
where id in (select distinct id
from nodes_tags where key = 'cuisine')
and key = 'amenity'
group by value
order by count(*) desc
'''
c.execute(query)
rows = c.fetchall()
pprint.pprint(rows)


# In[7]:

# Identify words used as well in type as in key or value fields.

query = '''
select axis, count(*)
from (select distinct type as axis from nodes_tags
UNION ALL select distinct key as axis from nodes_tags
UNION ALL select distinct value as axis from nodes_tags)
group by axis
having count(*) > 1
order by count(*) desc
limit 10;
'''
c.execute(query)
rows = c.fetchall()
pprint.pprint(rows)


# In[ ]:



