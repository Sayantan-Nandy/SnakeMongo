import mongoengine

def global_init_mongo():
    mongoengine.register_connection(alias="core",name="snake_bnb")

