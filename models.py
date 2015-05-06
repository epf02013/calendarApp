dbName= 'couchbase://localhost/calendarDb'

class user(object):
    def _init_(self, firstName, lastName, email, age, doc=None):
        self.firstName=firstName
        self.lastName=lastName
        self.email=email
        self.age=age
        if doc and doc.success:
            doc=doc.value
        else:
            doc=None
            self.doc=doc
