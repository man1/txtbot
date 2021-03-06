import sqlite3, sys
from util import *
ROULETTE_DATABASE = "roulette.db"

if __name__ == "__main__":
  db = sqlite3.connect(ROULETTE_DATABASE)
  cur = db.cursor()

  #### concatenate texts
  if len(sys.argv) > 1 and sys.argv[1] == "cat":
    # cat id1 id2
    if len(sys.argv) == 4:
      print "concatenating %s and %s" % (sys.argv[2], sys.argv[3])
      if cat_entries(int(sys.argv[2]), int(sys.argv[3]), db):
        print "success"
      else:
        print "no dice"
    else:
      print "arguments invalid for cat"

  #### simulate SMS arrival
  elif len(sys.argv) > 1 and sys.argv[1] == "sim":
    # sim txt origin [store] [reply] [reply_to_id]
    if len(sys.argv) > 3:
      # get all params
      txt = sys.argv[2]
      origin = sys.argv[3]
      store = True
      reply = True
      reply_to_id = -1
      if len(sys.argv) > 4:
        store = sys.argv[4] == "1"
      if len(sys.argv) > 5:
        reply = sys.argv[5] == "1"
      if len(sys.argv) > 6:
        reply_to_id = int(sys.argv[6])
      # friendly output
      print "simulating text message: \n\ttext: %s \n\torigin: %s\n\tstore: %s\n\treply: %s\n\treply to: %s" % \
        (txt, origin, "yes" if store else "no", "yes" if reply else "no", "last" if reply_to_id < 0 else str(reply_to_id))
      # store it
      if store:
        add_entry(txt, origin, db, True)
      # send it
      if reply:
        to = None;
        if reply_to_id < 0:
          # send to most recent
          to = get_recent(origin, db)['origin']
        else:
          # send to number of ID specified
          cur.execute("select origin from entries where id=?", [reply_to_id])
          to = cur.fetchone()[0]
        send_sms(txt, to)

    else:
      print "arguments invalid for sim"

  #### block a certain number
  elif len(sys.argv) > 1 and sys.argv[1] == "block":
    if len(sys.argv) > 2:
      remove = False
      to_block = sys.argv[2]
      if len(sys.argv) > 3 and sys.argv[3] == "remove": remove = True
      print "blocking %s removing all entries from %s" % ("and" if remove else "and NOT", to_block)
      # add to blocked table
      cur.execute("insert into blocked (num) values (?)", [to_block])
      # remove entries if need be
      if remove:
        cur.execute("delete from entries where origin=?", [to_block])
      db.commit()
    else:
      print "arguments invalid for block"

  #### create an entry in the best table
  elif len(sys.argv) > 1 and sys.argv[1] == "best":
    if len(sys.argv) > 3:
      first = sys.argv[2]
      last = sys.argv[3]
      print "marking entries %s through %s as a best" % (first, last)
      cur.execute("insert into best (first, last) values (?, ?)", [first, last])
      db.commit()
    else:
      print "arguments invalid for best"

  #### easily print out the last 10 posts
  elif len(sys.argv) > 1 and sys.argv[1] == "latest":
    n = 10 if len(sys.argv) < 3 else sys.argv[2]
    cur.execute("select * from entries order by id desc limit ?", [n])
    for l in cur.fetchall():
      print "%d\t%d\t%s\t%s" % (l[0], l[2], l[3], l[1])

  else:
    print """
      cat id1 id2
      sim txt origin [store?] [reply?] [reply_to_id]
      block number [remove]
      best first last
      latest [number]
    """
  # cat_entries(3, 1, db)
  db.close()