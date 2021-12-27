from pathlib import Path
from peewee import Model, ForeignKeyField, BooleanField, CompositeKey, CharField, IntegerField, TextField
from peewee import SqliteDatabase
from utils import file_utils


cwd = None
if Path.cwd().name == 'LavoroTesi':
    cwd = Path.cwd()
elif Path.cwd().parent.name == 'LavoroTesi':
    cwd = Path.cwd().parent
elif Path.cwd().parent.parent.name == 'LavoroTesi':
    cwd = Path.cwd().parent.parent
else:
    cwd = Path.cwd().parent.parent.parent
db_file = file_utils.set_file_in_folder('output', 'results.sqlite', cwd)
db_file.open(mode='a').close()
db = SqliteDatabase(str(db_file))
db.connect()


def handle_tables_creation():       # execute at the end of the file
    if len(db.get_tables()) > 18:
        pass
    else:
        db.create_tables([
            BaseModel,
            DomainNameEntity,
            UrlEntity,
            AliasAssociation,
            WebSiteEntity,
            WebServerEntity,
            WebServerDomainNameAssociation,
            WebSiteLandsAssociation,
            ZoneEntity,
            NameserverEntity,
            ZoneComposedAssociation,
            ZoneLinksAssociation,
            NameDependenciesAssociation,
            MailDomainEntity,
            MailserverEntity,
            MailDomainComposedAssociation,
            ScriptEntity,
            ScriptWithdrawAssociation,
            ScriptSiteEntity,
            ScriptHostedOnAssociation,
            ScriptServerEntity,
            ScriptSiteLandsAssociation,
            ScriptServerDomainNameAssociation,
            IpAddressEntity,
            AccessAssociation,
            IpNetworkEntity,
            AddressDependencyAssociation,
            AutonomousSystemEntity,
            ROVEntity,
            BelongsAssociation,
            PrefixesTableAssociation],    # 30 entities and associations
            safe=True)


def close_database():
    db.close()


class BaseModel(Model):
    class Meta:
        database = db


class DomainNameEntity(BaseModel):
    name = CharField(primary_key=True)

    def __str__(self):
        return f"<{self.name}>"

    class Meta:
        db_table = 'domain_name'


class UrlEntity(BaseModel):
    string = CharField(primary_key=True)

    def __str__(self):
        return f"<{self.string}>"

    class Meta:
        db_table = 'url'


class AliasAssociation(BaseModel):
    name = ForeignKeyField(DomainNameEntity)
    alias = ForeignKeyField(DomainNameEntity)

    def __str__(self):
        return f"<{self.name}, {self.alias}>"

    class Meta:
        primary_key = CompositeKey('name', 'alias')
        db_table = 'alias'


class WebSiteEntity(BaseModel):
    url = ForeignKeyField(UrlEntity)

    def __str__(self):
        return f"<{self.url}>"

    class Meta:
        db_table = 'website'


class WebServerEntity(BaseModel):
    url = ForeignKeyField(UrlEntity)

    def __str__(self):
        return f"<{self.url}>"

    class Meta:
        db_table = 'webserver'


class WebServerDomainNameAssociation(BaseModel):
    webserver = ForeignKeyField(WebServerEntity)
    domain_name = ForeignKeyField(DomainNameEntity)

    def __str__(self):
        return f"<{self.webserver}, {self.domain_name}>"

    class Meta:
        primary_key = CompositeKey('webserver', 'domain_name')
        db_table = 'webserver_domain_name'


class WebSiteLandsAssociation(BaseModel):
    website = ForeignKeyField(WebSiteEntity)
    webserver = ForeignKeyField(WebServerEntity, null=True)
    https = BooleanField(null=False)

    def __str__(self):
        return f"<{self.website}, {self.webserver}, {self.https}>"

    class Meta:
        db_table = 'website_lands'
        primary_key = CompositeKey('website', 'webserver', 'https')


class ZoneEntity(BaseModel):
    name = CharField(primary_key=True)

    def __str__(self):
        return f"<{self.name}>"

    class Meta:
        db_table = 'zone'


class NameserverEntity(BaseModel):
    name = ForeignKeyField(DomainNameEntity)

    def __str__(self):
        return f"<{self.name}>"

    class Meta:
        db_table = 'nameserver'


class ZoneComposedAssociation(BaseModel):
    zone = ForeignKeyField(ZoneEntity)
    nameserver = ForeignKeyField(NameserverEntity)

    def __str__(self):
        return f"<{self.name}>"

    class Meta:
        db_table = 'zone_composed'
        primary_key = CompositeKey('zone', 'nameserver')


class ZoneLinksAssociation(BaseModel):
    zone = ForeignKeyField(ZoneEntity)
    dependency = ForeignKeyField(ZoneEntity)

    def __str__(self):
        return f"<{self.zone}, {self.dependency}>"

    class Meta:
        db_table = 'zone_links'
        primary_key = CompositeKey('zone', 'dependency')


class NameDependenciesAssociation(BaseModel):
    domain_name = ForeignKeyField(DomainNameEntity)
    zone = ForeignKeyField(ZoneEntity)

    def __str__(self):
        return f"<{self.domain_name}, {self.zone}>"

    class Meta:
        db_table = 'name_dependencies'
        primary_key = CompositeKey('domain_name', 'zone')


class MailDomainEntity(BaseModel):
    name = ForeignKeyField(DomainNameEntity)

    def __str__(self):
        return f"<{self.name}>"

    class Meta:
        db_table = 'mail_domain'


class MailserverEntity(BaseModel):
    name = ForeignKeyField(DomainNameEntity)

    def __str__(self):
        return f"<{self.name}>"

    class Meta:
        db_table = 'mailserver'


class MailDomainComposedAssociation(BaseModel):
    mail_domain = ForeignKeyField(MailDomainEntity)
    mailserver = ForeignKeyField(MailserverEntity)

    def __str__(self):
        return f"<{self.mail_domain}, {self.mail_domain}>"

    class Meta:
        db_table = 'mail_domain_composed'
        primary_key = CompositeKey('mail_domain', 'mailserver')


class ScriptEntity(BaseModel):
    src = CharField(primary_key=True)
    mime_type = CharField(null=False)

    def __str__(self):
        return f"<{self.src}, {self.mime_type}>"

    class Meta:
        db_table = 'script'


class ScriptWithdrawAssociation(BaseModel):
    script = ForeignKeyField(ScriptEntity)
    website = ForeignKeyField(WebSiteEntity)
    integrity = CharField(null=True)

    def __str__(self):
        return f"<{self.script}, {self.website}, {self.integrity}>"

    class Meta:
        db_table = 'script_withdraw'
        primary_key = CompositeKey('script', 'website')


class ScriptSiteEntity(BaseModel):
    url = ForeignKeyField(UrlEntity)

    def __str__(self):
        return f"<{self.url}>"

    class Meta:
        db_table = 'script_site'


class ScriptHostedOnAssociation(BaseModel):
    script_site = ForeignKeyField(ScriptSiteEntity)
    script = ForeignKeyField(ScriptEntity)

    def __str__(self):
        return f"<{self.script_site}, {self.script}>"

    class Meta:
        db_table = 'script_hosted_on'
        primary_key = CompositeKey('script_site', 'script')


class ScriptServerEntity(BaseModel):
    url = ForeignKeyField(UrlEntity)

    def __str__(self):
        return f"<{self.url}>"

    class Meta:
        db_table = 'script_server'


class ScriptSiteLandsAssociation(BaseModel):
    script_site = ForeignKeyField(ScriptSiteEntity)
    script_server = ForeignKeyField(ScriptServerEntity)

    def __str__(self):
        return f"<{self.script_site}, {self.script_server}>"

    class Meta:
        db_table = 'scriptsite_lands'
        primary_key = CompositeKey('script_site', 'script_server')


class ScriptServerDomainNameAssociation(BaseModel):
    script_server = ForeignKeyField(ScriptServerEntity)
    domain_name = ForeignKeyField(DomainNameEntity)

    def __str__(self):
        return f"<{self.script_server}, {self.domain_name}>"

    class Meta:
        primary_key = CompositeKey('script_server', 'domain_name')
        db_table = 'website_domain_name'


class IpAddressEntity(BaseModel):
    exploded_notation = CharField(primary_key=True)

    def __str__(self):
        return f"<{self.exploded_notation}>"

    class Meta:
        db_table = 'ip_address'


class AccessAssociation(BaseModel):
    domain_name = ForeignKeyField(DomainNameEntity)
    ip_address = ForeignKeyField(IpAddressEntity)

    def __str__(self):
        return f"<{self.domain_name}, {self.ip_address}>"

    class Meta:
        db_table = 'access'


class IpNetworkEntity(BaseModel):
    compressed_notation = CharField(primary_key=True)

    def __str__(self):
        return f"<{self.compressed_notation}>"

    class Meta:
        db_table = 'ip_network'


class AddressDependencyAssociation(BaseModel):
    ip_address = ForeignKeyField(IpAddressEntity)
    ip_network = ForeignKeyField(IpNetworkEntity)

    def __str__(self):
        return f"<{self.ip_address}, {self.ip_network}>"

    class Meta:
        db_table = 'address_dependency'


class AutonomousSystemEntity(BaseModel):
    number = IntegerField(primary_key=True)

    def __str__(self):
        return f"<{self.number}>"

    class Meta:
        db_table = 'autonomous_system'


class ROVEntity(BaseModel):
    state = CharField(null=False)
    visibility = IntegerField(null=False)

    def __str__(self):
        return f"<{self.state}, {self.visibility}>"

    class Meta:
        db_table = 'rov'


class BelongsAssociation(BaseModel):
    ip_network = ForeignKeyField(IpNetworkEntity)
    autonomous_system = ForeignKeyField(AutonomousSystemEntity)

    def __str__(self):
        return f"<{self.ip_network}, {self.autonomous_system}>"

    class Meta:
        db_table = 'belongs'


class PrefixesTableAssociation(BaseModel):
    ip_network = ForeignKeyField(IpNetworkEntity)
    rov = ForeignKeyField(ROVEntity)
    autonomous_system = ForeignKeyField(AutonomousSystemEntity)

    def __str__(self):
        return f"<{self.ip_network}, {self.rov}, {self.autonomous_system}>"

    class Meta:
        db_table = 'prefixes_table'
        primary_key = CompositeKey('ip_network', 'rov', 'autonomous_system')


handle_tables_creation()
