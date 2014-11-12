import couchdb
import flask.ext.login

couch = None
db = None

def init_db(config):
    global couch, db
    if couch or db:
        raise RuntimeError("DB is already initialized")
    couch = couchdb.Server(config['DB_URL'])
    if 'chimera_users' in couch:
        db = couch['chimera_users']
    else:
        db = couch.create('chimera_users')
    if not(config['SUPER_ADMIN'] in db):
        db.save({"_id": config['SUPER_ADMIN'], "super_admin": True})

class User(flask.ext.login.UserMixin):
    @staticmethod
    def get(email):
        return User(email)

    def __init__(self, email):
        self.id = email
        if self.id in db:
            doc = db[self.id]
        else:
            doc = {}
        self.access_token = doc.get('access_token', None)
        self.super_admin = doc.get('super_admin', False)
        self.permissions = doc.get('permissions', {})
        self._rev = doc.get('_rev', None)

    def save(self):
        doc = {"_id": self.id, "_rev": self._rev, "access_token":
                self.access_token, "super_admin": self.super_admin,
                "permissions": self.permissions}
        db.save(doc)

    def is_active(self):
        return self.has_permission("login")

    def has_permission(self, permission):
        if self.super_admin:
            return True
        cur = self.permissions
        for node in permission.split(":"):
            if node in cur:
                cur = cur[node]
            elif '*' in cur:
                return cur['*']
            elif cur == True:
                return True
            else:
                return False
        return not(not(cur))
