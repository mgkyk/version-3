"""
this is the logic of the server
# Log: login, get the privilege
# MachineList: all the info of the Machine
# Machine: a Single Machine
# MachineList_Source: source for the MachineList
# Machine_Source: source for the singe Machine

# author: ChuXiaokai
# date: 2016/3/24
"""
from flask import Flask, request, jsonify, g, abort
from flask.ext.httpauth import HTTPBasicAuth
from flask.ext.sqlalchemy import SQLAlchemy
from passlib.apps import custom_app_context as pwd_context
import server
host = server.Server()  # server
auth = HTTPBasicAuth()
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///webappdb'
app.config['SQLALCHEMY_COMMIT_ON_TEARDOWN'] = True
db = SQLAlchemy(app)

### Queue ##############################################################################
q = []  # for the second verify, to deny for: -u user1:user1.passwd http://xxx/user2

def second_verify(user_id):
    current_user = q.pop()
    if current_user == user_id:
        return True
    else:
        return False
    
### database ###########################################################################
# table User
class User(db.Model):
    user = db.Column(db.String(40), primary_key=True)
    password_hash = db.Column(db.String(40))  # password need to be hashed before installed
    num_mcs = db.Column(db.Integer)

    def __init__(self, user, passwd=0):
        self.user = user
        self.passwd = passwd
        self.num_mcs = 0

    def verify_password(self, password):
        return pwd_context.verify(password, self.password_hash)

    def hash_password(self, password):
        self.password_hash =  pwd_context.encrypt(password)    


# table VM_machine
class VM_machine(db.Model):
    mc_id = db.Column(db.String(40), primary_key=True)
    user = db.Column(db.String(40))
    connect_info = db.Column(db.String(100))

    def __init__(self, mc_id, user, connect_info):
        self.mc_id = mc_id
        self.connect_info = connect_info
        self.user = user

    def __repr__(self):
        return '<mc_id %r>' % self.mc_id


# table Resource
class Resource(db.Model):
    source_name = db.Column(db.String(40), primary_key=True)
    map = db.Column(db.String(40))
    shell_path = db.Column(db.String(100))
    detail = db.Column(db.String(100))

    def __init__(self, source_name, map, shell_path, detail):
        self.source_name = source_name
        self.map = map
        self.shell_path = shell_path
        self.detail = detail

    def __repr__(self):
        return '<source_name %r>' % self.source_name

### web app ############################################################################
@auth.verify_password
def verify_password(username_or_token, password):
    q.append(username_or_token)
    user = User.query.filter_by(user=username_or_token).first()  # find if the user exists
    if not user or not user.verify_password(password):
        return False
    g.user = user
    return True


# get a new user id
@app.route('/newuser', methods=['POST'])
def post_newuser():
    user = request.form['user']
    passwd = request.form['passwd']
    if user is None or passwd is None:  # if query missing user or passwd
        abort(400)
    a = db.session.query(User).filter(User.user == user).first()
    if db.session.query(User).filter(User.user==user).first() is not None:  # this user has existed
        abort(400)
    new_user = User(user=user)  # append a recode
    new_user.hash_password(passwd)
    db.session.add(new_user)
    db.session.commit()
    return (jsonify({'user': new_user.user}))


# get a user info
@app.route('/<string:user_id>', methods=['GET'])
@auth.login_required
def get_user_info(user_id):
    if second_verify(user_id) == False:
        abort(400)
    admin = db.session.query(User).filter(User.user==user_id).first()
    return (jsonify({'userinfo': [{'user_id':admin.user}, {'num_mcs':admin.num_mcs}]}))


# get a new mc
@app.route('/<string:user_id>', methods=['POST'])
@auth.login_required
def get_new_mc(user_id):
    if second_verify(user_id) == False:
        abort(400)
    mc_id, passwd, mc_ip = host.init_machine()
    connect_info =  'host: %s  passwd: %s  machine_ip: %s' % (host.ip, passwd, mc_ip)
    new_mc = VM_machine(mc_id, user_id, connect_info)
    db.session.add(new_mc)
    db.session.query(User).filter(User.user==user_id).update({User.num_mcs:User.num_mcs+1})
    db.session.commit()
    return (jsonify({'mc_info': [{'mc_id': mc_id, 'ip': mc_ip, 'passwd': passwd}]}))


# get user's mc list
@app.route('/<string:user_id>/mcs', methods=['GET'])
@auth.login_required
def get_machine_list(user_id):
    if second_verify(user_id) == False:
        abort(400)
    a = db.session.query(VM_machine).filter(VM_machine.user==user_id).all()
    user_machines = []
    for i in range(len(a)):
        tmp = {"mc_id": a[i].mc_id, "user": a[i].user, "connect_info": a[i].connect_info}
        user_machines.append(tmp)
    return (jsonify({'user_machines': user_machines}))


# get user's a mc info
@app.route('/<string:user_id>/<string:mc_id>', methods=['GET'])
@auth.login_required
def get_machine(user_id, mc_id):
    if second_verify(user_id) == False:
        abort(400)
    mc_info = db.session.query(VM_machine).filter(VM_machine.user==user_id and VM_machine.mc_id == mc_id).first()
    current_state = host.get_machine_state(mc_id) 
    return (jsonify({'machine_info': [{"mc_id": mc_info.mc_id, "user": mc_info.user, "connect_info": mc_info.connect_info}], 'current state': [current_state]}))


# delete user's a mc
@app.route('/<string:user_id>/<string:mc_id>', methods=['DELECT'])
@auth.login_required
def delect_machine(user_id, mc_id):
    if second_verify(user_id) == False:
        abort(400)
    host.kill_machine(mc_id)  # kill a mc
    # delete it in the database
    recode = db.session.query(VM_machine).filter(VM_machine.mc_id == mc_id).first()
    db.session.delete(recode)
    # update user information
    db.session.query(User).filter(User.user==user_id).update({User.num_mcs:User.num_mcs-1})
    return (jsonify({'state': 'current'"delete '%s' successfully !" % mc_id}))


# get resource list
@app.route('/srclist', methods=['GET'])
def get_source_list():
    recodes = db.session.query(Resource).all()
    sources_info = []
    for i in range(len(recodes)):
        tmp = {'source_name': recodes[i].source_name, 'detail': recodes[i].detail}
        sources_info.append(tmp)
    return (jsonify({'Sources Available': sources_info}))


# get a resource info
@app.route('/srclist/<string:src_name>', methods=['GET'])
def get_source(src_name):
    recode = db.session.query(Resource).filter(Resource.source_name==src_name).first()
    return (jsonify({'source_info': [{'source_name': recode.source_name, 'detail': recode.detail}]}))


# install a resource in a mc
@app.route('/srclist/<string:user_id>/<string:src_name>', methods=['POST'])
@auth.login_required
def install_source(user_id, src_name):
    if second_verify(user_id) == False:
        abort(400)
        
    def filter_space(x):  # this func f(x) is used for the filter
            if x != [] and x != " ":
                return x
        
    form = request.form['form']
    mc = request.form['mc']
    # get the shell path
    recode = db.session.query(Resource).filter(Resource.source_name == src_name).first()
    shell_path = recode.shell_path
    # execute the shell
    if form == 'cluster':
        mc_param = mc.split(' ')
        mc_param = [item for item in filter(filter_space, mc_param)]  # filter the [] in mc_param
        if host.exec_shell(shell_path=shell_path, param=mc_param, state='cluster') == True: # install a cluster
            return (jsonify({'state': "Success install"}))
        else:
            return (jsonify({'state': "Fail to install"}))
    elif form == 'single_node':
        mc_param = mc
        if host.exec_shell(shell_path=shell_path, param=mc_param, state='single') == True:  # install a single node
            return (jsonify({'state': "Success install"}))
        else:
            return (jsonify({'state': "Fail to install"}))


if __name__ == '__main__':
    db.create_all()
    app.run(debug=True)
