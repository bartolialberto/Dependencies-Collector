from pathlib import Path
from peewee import Model, ForeignKeyField, BooleanField, CompositeKey, CharField, IntegerField, TextField
from peewee import SqliteDatabase
from utils import file_utils


cwd = None
if Path.cwd().name == 'LavoroTesi':
    cwd = Path.cwd()
else:
    cwd = Path.cwd().parent
db_file = file_utils.set_file_in_folder('output', 'results.sqlite', cwd)
db_file.open(mode='a').close()
db = SqliteDatabase(str(db_file))
db.connect()


def handle_tables_creation():       # execute at the end of the file
    if len(db.get_tables()) > 10:
        pass
    else:
        db.create_tables([BaseModel,
                          DomainNameEntity,
                          ZoneEntity,
                          DependsAssociation,
                          BelongsAssociation,
                          NameserverEntity,
                          PageEntity,
                          LandingPageEntity,
                          LandsAssociation,
                          RedirectionPath,
                          ContentDependencyEntity,
                          ContentDependencyAssociation,
                          IpNetworkEntity,
                          EntryIpAsDatabaseEntity,
                          EntryROVPageEntity,
                          PrefixAssociation,
                          BelongingNetworkAssociation,
                          MatchesAssociation], safe=True)


class BaseModel(Model):
    class Meta:
        database = db


class NameserverEntity(BaseModel):
    name = CharField(null=False)
    ip = CharField(null=True)

    def __str__(self):
        return f"<{self.name}, {self.ip}>"

    class Meta:
        db_table = 'nameserver'


class DomainNameEntity(BaseModel):
    name = CharField(null=False)

    def __str__(self):
        return f"<{self.name}>"

    class Meta:
        db_table = 'domain_name'


class ZoneEntity(BaseModel):
    name = CharField(null=False)

    def __str__(self):
        return f"<{self.name}>"

    class Meta:
        db_table = 'zone'


class BelongsAssociation(BaseModel):
    zone = ForeignKeyField(ZoneEntity)
    nameserver = ForeignKeyField(NameserverEntity)

    def __str__(self):
        return f"<{self.zone}, {self.nameserver}>"

    class Meta:
        primary_key = CompositeKey('zone', 'nameserver')
        db_table = 'belongs'


class DependsAssociation(BaseModel):
    domain = ForeignKeyField(DomainNameEntity)
    zone = ForeignKeyField(ZoneEntity)

    def __str__(self):
        return f"<{self.domain}, {self.zone}>"

    class Meta:
        primary_key = CompositeKey('domain', 'zone')
        db_table = 'depends'


class PageEntity(BaseModel):
    url = CharField(null=False)
    hsts = BooleanField(null=False)

    def __str__(self):
        return f"<{self.url}, {self.hsts}>"

    class Meta:
        db_table = 'page'


class LandingPageEntity(BaseModel):
    page = ForeignKeyField(PageEntity)

    def __str__(self):
        return f"<{self.page}>"

    class Meta:
        db_table = 'landing_page'


class LandsAssociation(BaseModel):
    domain_name = ForeignKeyField(DomainNameEntity)
    landing_page = ForeignKeyField(LandingPageEntity)

    def __str__(self):
        return f"<{self.domain_name}, {self.landing_page}>"

    class Meta:
        primary_key = CompositeKey('domain_name', 'landing_page')
        db_table = 'lands'


class RedirectionPath(BaseModel):
    landing_page = ForeignKeyField(PageEntity)
    page = ForeignKeyField(PageEntity)

    def __str__(self):
        return f"<{self.landing_page}, {self.page}>"

    class Meta:
        primary_key = CompositeKey('landing_page', 'page')
        db_table = 'redirection_path'


class ContentDependencyEntity(BaseModel):
    url = CharField(null=False)
    mime_type = CharField(null=False)
    state = CharField(null=False)
    domain_name = CharField(null=False)

    def __str__(self):
        return f"<{self.url}, {self.mime_type}, {self.state}, {self.domain_name}>"

    class Meta:
        db_table = 'content_dependency'


class ContentDependencyAssociation(BaseModel):
    landing_page = ForeignKeyField(LandingPageEntity)
    content_dependency_entity = ForeignKeyField(ContentDependencyEntity)

    def __str__(self):
        return f"<{self.landing_page}, {self.content_dependency_entity}>"

    class Meta:
        db_table = 'uses'


class IpNetworkEntity(BaseModel):
    compressed_notation = CharField(null=False)

    def __str__(self):
        return f"<{self.compressed_notation}>"

    class Meta:
        db_table = 'network_ip'


class EntryIpAsDatabaseEntity(BaseModel):
    autonomous_system_number = IntegerField(null=False)
    start_range_ip = CharField(null=False)
    end_range_ip = CharField(null=False)
    country_code = CharField(null=True)     # some are None
    autonomous_system_description = TextField(null=False)

    def __str__(self):
        return f"<{self.start_range_ip}, {self.end_range_ip}, {str(self.autonomous_system_number)}, {self.country_code}, {self.autonomous_system_description}>"

    class Meta:
        db_table = 'entry_ip_as_db'


class EntryROVPageEntity(BaseModel):
    autonomous_system_number = IntegerField( null=False)
    visibility = IntegerField(null=False)
    rov_state = CharField(null=False)       # create a CustomField for enum: ROVState ?

    def __str__(self):
        return f"<{self.start_range_ip}, {self.end_range_ip}, {str(self.autonomous_system_number)}, {self.country_code}, {self.autonomous_system_description}>"

    class Meta:
        db_table = 'entry_rov_page'


class PrefixAssociation(BaseModel):
    entry = ForeignKeyField(EntryROVPageEntity)
    network = ForeignKeyField(IpNetworkEntity)

    def __str__(self):
        return f"<{self.entry}, {self.network}>"

    class Meta:
        primary_key = CompositeKey('entry', 'network')
        db_table = 'prefix'


class BelongingNetworkAssociation(BaseModel):
    entry = ForeignKeyField(EntryIpAsDatabaseEntity)
    network = ForeignKeyField(IpNetworkEntity)

    def __str__(self):
        return f"<{self.entry}, {self.network}>"

    class Meta:
        primary_key = CompositeKey('entry', 'network')
        db_table = 'belonging_network'


class MatchesAssociation(BaseModel):
    nameserver = ForeignKeyField(NameserverEntity)
    entry_ip_as_database = ForeignKeyField(EntryIpAsDatabaseEntity, null=True)
    entry_rov_page = ForeignKeyField(EntryROVPageEntity, null=True)

    def __str__(self):
        return f"<{self.nameserver}, {self.entry_ip_as_database}, {self.entry_rov_page}>"

    class Meta:
        primary_key = CompositeKey('nameserver', 'entry_ip_as_database', 'entry_rov_page')
        db_table = 'matches'


handle_tables_creation()
