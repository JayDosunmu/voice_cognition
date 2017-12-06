class Users:
    def __init__(self):
        self.users = {}
        self.new_id = 0


    def all_users(self):
        return self.users


    def all_users_v_ids(self):
        v_ids = []
        for u_id, user in self.users.items():
            v_ids.append(user.get_v_id())
        return v_ids


    def new_user(self, name):
        user = User(name)
        user.set_id(self.new_id)

        self.users[self.new_id] = user
        self.new_id += 1
        return user


    def add_user(self, user):
        self.users[user.get_id()] = user


    def edit_user(self, id, **kwargs):
        user = self.get_user_by_id(id)
        
        if user:
            user.set_name(kwargs.get('name', user.get_name()))
            user.set_v_id(kwargs.get('v_id', user.get_v_id()))
        else:
            return False


    def get_user_by_id(self, id):
        return self.users.get('id', None)

    
    def get_user_by_v_id(self, v_id):
        for id, user in self.users.items():
            if user.get_v_id() == v_id:
                return user

        return None


class User:
    def __init__(self, name):
        self.name = name
        self.id = None
        self.v_id = None


    def set_name(self, name):
        self.name = name


    def set_id(self, id):
        self.id = id


    def set_v_id(self, v_id):
        self.v_id = v_id

    
    def get_id(self):
        return self.id

    
    def get_v_id(self):
        return self.v_id

    
    def get_name(self):
        return self.name