import lib.database

db = database.Database()

def printa(x):
  print x

db.save_event('teste', {"field1": "cenas1", "field2": "outra1"})
db.save_event('teste', {"field1": "cenas2", "field2": "outra1"})
db.save_event('teste', {"field1": "cenas3", "field2": "outra2"})
db.save_event('teste', {"field1": "cenas4", "field2": "outra3"})
db.save_event('teste', {"field1": "cenas5", "field2": "outra3"})

print 'UUUUUUUUUUUUUUUUUUUUUUUUU'
map(printa, db.get_events("teste"))
print 'AAAAAAAAAAAAAAAAAAAAAAAAA'
print db.get_distinct("teste", "field1", "field2")
print 'BBBBBBBBBBBBBBBBBBBBBBBBB'
