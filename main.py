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

from flask import Flask
from flask_restful import reqparse, abort, Api, Resource
from database import ServerDatabase
import server

# database point
db = ServerDatabase()

# server point
host = server.Server()

# parse the parameter
parser = reqparse.RequestParser()
parser.add_argument('user', type=str, help='user name should be a string')
#parser.add_argument('passwd', type=int, required=True)
parser.add_argument('passwd', type=str)
parser.add_argument('mc', type=str)
parser.add_argument('form', type=str)

# Regist
# /newuser
class New_User(Resource):
    def post(self):
        """
        :return:
        """
        args = parser.parse_args()
        user = args['user']
        passwd = args['passwd']

        # database operate
        if db.conn.open == False:  # check for if the connection is open
            db.connect()

        try:
            db.cursor.execute('USE webapp')
            db.cursor.execute('INSERT INTO account (user, passwd, num_mcs) VALUES("%s", "%s", "%d")' % (user, passwd, 0))
            db.conn.commit()
            return [user, passwd], 200
        except:
            print("Failed to insert data")
            return "Failed to insert data"



# Login
class Login(Resource):
    def post(self):
        """
        :return: login
        """


# User
# show the information of the user(distinguish manager and consumer;)
# /user_id
class User(Resource):
    def get(self, user_id):
        """
        :param userid:
        :return: get the info of the user, including, numbers of the mc, previlige
        """
        # database operate
        if db.conn.open == False:  # check for if the connection is open
            db.connect()
        try:
            db.cursor.execute('USE webapp')
            db.cursor.execute('select * from account where user="%s"' % user_id)
            user_info = db.cursor.fetchall()
            return user_info, 200
        except:
            print("Failed to fetch data")
            return "Failed to fetch data"

    def post(self, user_id):
        """
        :return: apply for a new mc
        """
        # command in server
        mc_id, passwd, mc_ip = host.init_machine()
        connect_info =  'host: %s  passwd: %s  machine_ip: %s' % (host.ip, passwd, mc_ip)
        print(mc_id, passwd, connect_info)

        # database operate
        if db.conn.open == False:
            db.connect()
        try:
            db.cursor.execute('USE webapp')
            db.cursor.execute('INSERT INTO docker (mc_id, user, connect_info) VALUES("%s", "%s", "%s")' % (mc_id, user_id,  connect_info))
            db.cursor.execute('UPDATE account SET num_mcs=num_mcs+1 where user="%s"' % (user_id))
            db.conn.commit()
            return "NEW MACHINE:'%s', mc_id IP: '%s' passwd:'%s'" % (mc_id, mc_ip, passwd)
        except:
            return "Failed to get a mc"


# MachineList
# show a list of mcs and it's status()
# /<string:user_id>/mcs>
class MachineList(Resource):
    def get(self, user_id):
        if db.conn.open == False:
            db.connect()
        try:
            db.cursor.execute('Use webapp')
            db.cursor.execute('SELECT * FROM docker WHERE user="%s"' % user_id)
            machines_info = db.cursor.fetchall()
            return machines_info
        except:
            return  "Failed to get the info"


# Machine
# show a single mc
# /<string:user_id>/<int:mc_id>
class Machine(Resource):
    def get(self, user_id, mc_id):
        """
        :return: get the information of the machine, including the deployments and environment
        """
        # database operate
        if db.conn.open == False:
            db.connect()
        try:
            db.cursor.execute('Use webapp')
            db.cursor.execute('SELECT * FROM docker WHERE mc_id="%s" and user="%s"' % mc_id, user_id)
            mc_info = db.cursor.fetchall()
            return mc_info
        except:
            return "Failed to fetch information"


    def delete(self, user_id, mc_id):
        """
		delete a machine
		"""
        host.kill_machine(mc_id)

        # database operate
        if db.conn.open == False:
            db.connect()

        try:
            db.cursor.execute('USE webapp')
            db.cursor.execute('DELETE FROM docker WHERE mc_id=%s and user=%s' % mc_id, user_id)
            db.cursor.execute('UPDATE account SET num_mcs=num_macs-1 WHERE user=%s' % user_id)
            db.conn.commit()
        except:
            return "Failed to delete mc"

# Source
# show a list of source
# /<string:user_id>/srclist
class SourceList(Resource):
    def get(self):
        """
        get a list of source available
        """
        # database operate
        if db.conn.open == False:
            db.connect()
        try:
            db.cursor.execute('USE webapp')
            db.cursor.execute('SELECT * FROM source')
            source_info_list = db.cursor.fetchall()
            ret_info = {}  # type=json
            for i in range(len(source_info_list)):  # insert data
                ret_info[source_info_list[i][0]] = source_info_list[i][3]

            return ret_info
        except:
            return "Failed to fetch information"

    def put(self):
        """
        add a source(root)
        """
        pass


# src_id
# /<string:user_id>/srclist/<string:srcname>
class Source(Resource):
    def get(self):
        """
        get the info of the source
        :return:
        """
        if db.conn.open == False:
            db.connect()

        try:  # get the path where the shell located
            db.cursor.execute('USE webapp')
            db.cursor.execute('SELECT source_name, detail FROM source')
            return db.cursor.fetchall()
        except:
            return "Failed to get the shell"


    def delete(self):
        """
        only for the root
        :return:
        """

    def post(self, user_id, src_name):
        """
        install source on the mc(using some algorithm)
        form: curl -d "form=cluster" -d "mc=123123 134234 3242 2342" http://xxx/srclist/cxk/mysql
        """
        def filter_space(x):  # this func f(x) is used for the filter
            if x != [] and x != " ":
                return x

        args = parser.parse_args()
        form = args['form']  # can be a cluster or a single node
        mc = args['mc']
        print(form, mc)
        
        if db.conn.open == False:
            db.connect()

        try:  # get the path where the shell located
            db.cursor.execute('USE webapp')
            db.cursor.execute('SELECT shell_path FROM source WHERE source_name="%s"' % src_name)
            shell_path = db.cursor.fetchall()[0][0]
        except:
            return "Failed to get the shell"

        # execute the shell
        if form == 'cluster':
            mc_param = mc.split(' ')
            mc_param = [item for item in filter(filter_space, mc_param)]  # filter the [] in mc_param
            if host.exec_shell(shell_path=shell_path, param=mc_param, state='cluster') == True: # install a cluster
                return "Success install"
            else:
                return "Fail to install"

        elif form == 'single_node':
            mc_param = mc
            print(mc_param)
            if host.exec_shell(shell_path=shell_path, param=mc_param, state='single') == True:  # install a single node
                return "Success install"
            else:
                return "Fail to install"


def init_web_app():
    app = Flask(__name__)
    api = Api(app)
    #  setup the api resource routing here
    api.add_resource(New_User, '/newuser', endpoint='newuser')
    api.add_resource(User, '/<string:user_id>', endpoint='user')
    api.add_resource(MachineList, '/<string:user_id>/mcs', endpoint='mcs')
    api.add_resource(Machine, '/<string:user_id>/<string:mc_id>', endpoint='mc')
    api.add_resource(SourceList, '/srclist', endpoint='srclist')
    api.add_resource(Source, '/srclist/<string:user_id>/<string:src_name>', endpoint='srcname')
    return app


if __name__ == '__main__':
    app = init_web_app()
    app.run()

