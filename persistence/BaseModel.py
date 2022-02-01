from pathlib import Path
from peewee import Model, ForeignKeyField, BooleanField, CompositeKey, CharField, IntegerField, TextField
from peewee import SqliteDatabase
from utils import file_utils


project_root_directory_name = 'LavoroTesi'
cwd = None
if Path.cwd().name == project_root_directory_name:
    cwd = Path.cwd()
elif Path.cwd().parent.name == project_root_directory_name:
    cwd = Path.cwd().parent
elif Path.cwd().parent.parent.name == project_root_directory_name:
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
            WebSiteLandsAssociation,
            ZoneEntity,
            NameServerEntity,
            ZoneComposedAssociation,
            ZoneLinksAssociation,
            DomainNameDependenciesAssociation,
            DirectZoneAssociation,
            MailDomainEntity,
            MailServerEntity,
            MailDomainComposedAssociation,
            ScriptEntity,
            ScriptWithdrawAssociation,
            ScriptSiteEntity,
            ScriptHostedOnAssociation,
            ScriptServerEntity,
            ScriptSiteLandsAssociation,
            IpAddressEntity,
            AccessAssociation,
            IpNetworkEntity,
            IpRangeTSVEntity,
            IpRangeROVEntity,
            IpAddressDependsAssociation,
            AutonomousSystemEntity,
            ROVEntity,
            PrefixesTableAssociation,
            NetworkNumbersAssociation,
            ScriptSiteDomainNameAssociation,
            WebSiteDomainNameAssociation,
            AliasToZoneAssociation],    # 33 entities and associations
            safe=True)


def close_database():
    db.close()


class BaseModel(Model):
    class Meta:
        database = db


class DomainNameEntity(BaseModel):
    string = CharField(primary_key=True)

    def __str__(self):
        return f"<string={self.string}>"

    class Meta:
        db_table = 'domain_name'


class UrlEntity(BaseModel):
    string = CharField(primary_key=True)

    def __str__(self):
        return f"<string={self.string}>"

    class Meta:
        db_table = 'url'


class IpAddressEntity(BaseModel):
    exploded_notation = CharField(primary_key=True)

    def __str__(self):
        return f"<exploded_notation={self.exploded_notation}>"

    class Meta:
        db_table = 'ip_address'


class WebSiteEntity(BaseModel):
    url = ForeignKeyField(UrlEntity)

    def __str__(self):
        return f"<url={self.url}>"

    class Meta:
        db_table = 'web_site'


class WebServerEntity(BaseModel):
    name = ForeignKeyField(DomainNameEntity)

    def __str__(self):
        return f"<name={self.name}>"

    class Meta:
        db_table = 'web_server'


class ZoneEntity(BaseModel):
    name = CharField(primary_key=True)

    def __str__(self):
        return f"<name={self.name}>"

    class Meta:
        db_table = 'zone'


class NameServerEntity(BaseModel):
    name = ForeignKeyField(DomainNameEntity)

    def __str__(self):
        return f"<name={self.name}>"

    class Meta:
        db_table = 'name_server'


class MailDomainEntity(BaseModel):
    name = ForeignKeyField(DomainNameEntity)

    def __str__(self):
        return f"<name={self.name}>"

    class Meta:
        db_table = 'mail_domain'


class MailServerEntity(BaseModel):
    name = ForeignKeyField(DomainNameEntity)

    def __str__(self):
        return f"<name={self.name}>"

    class Meta:
        db_table = 'mail_server'


class ScriptEntity(BaseModel):
    src = CharField(primary_key=True)

    def __str__(self):
        return f"<src={self.src}>"

    class Meta:
        db_table = 'script'


class ScriptSiteEntity(BaseModel):
    url = ForeignKeyField(UrlEntity)

    def __str__(self):
        return f"<url={self.url}>"

    class Meta:
        db_table = 'script_site'


class ScriptServerEntity(BaseModel):
    name = ForeignKeyField(DomainNameEntity)

    def __str__(self):
        return f"<name={self.name}>"

    class Meta:
        db_table = 'script_server'


class IpNetworkEntity(BaseModel):
    compressed_notation = CharField(primary_key=True)

    def __str__(self):
        return f"<compressed_notation={self.compressed_notation}>"

    class Meta:
        db_table = 'ip_network'


class IpRangeTSVEntity(BaseModel):
    compressed_notation = CharField(primary_key=True)

    def __str__(self):
        return f"<compressed_notation={self.compressed_notation}>"

    class Meta:
        db_table = 'ip_range_tsv'


class IpRangeROVEntity(BaseModel):
    compressed_notation = CharField(primary_key=True)

    def __str__(self):
        return f"<compressed_notation={self.compressed_notation}>"

    class Meta:
        db_table = 'ip_range_rov'


class AutonomousSystemEntity(BaseModel):
    number = IntegerField(primary_key=True)
    description = TextField()

    def __str__(self):
        return f"<number={self.number}, description={self.description}>"

    class Meta:
        db_table = 'autonomous_system'


class ROVEntity(BaseModel):
    state = CharField(null=False)
    visibility = IntegerField(null=False)

    def __str__(self):
        return f"<state={self.state}, visibility={self.visibility}>"

    class Meta:
        db_table = 'rov'


class AliasAssociation(BaseModel):
    name = ForeignKeyField(DomainNameEntity)
    alias = ForeignKeyField(DomainNameEntity)

    def __str__(self):
        return f"<name={self.name}, alias={self.alias}>"

    class Meta:
        primary_key = CompositeKey('name', 'alias')
        db_table = 'alias'


class WebSiteLandsAssociation(BaseModel):
    web_site = ForeignKeyField(WebSiteEntity)
    web_server = ForeignKeyField(WebServerEntity, null=True)
    https = BooleanField(null=False)

    def __str__(self):
        return f"<web_site={self.web_site}, web_server={self.web_server}, https={self.https}>"

    class Meta:
        db_table = 'web_site_lands'
        primary_key = CompositeKey('web_site', 'web_server', 'https')


class ZoneComposedAssociation(BaseModel):
    zone = ForeignKeyField(ZoneEntity)
    name_server = ForeignKeyField(NameServerEntity)

    def __str__(self):
        return f"<zone={self.zone}, name_server={self.name_server}>"

    class Meta:
        db_table = 'zone_composed'
        primary_key = CompositeKey('zone', 'name_server')


class ZoneLinksAssociation(BaseModel):
    zone = ForeignKeyField(ZoneEntity)
    dependency = ForeignKeyField(ZoneEntity)

    def __str__(self):
        return f"<zone={self.zone}, dependency={self.dependency}>"

    class Meta:
        db_table = 'zone_links'
        primary_key = CompositeKey('zone', 'dependency')


class DomainNameDependenciesAssociation(BaseModel):
    domain_name = ForeignKeyField(DomainNameEntity)
    zone = ForeignKeyField(ZoneEntity)

    def __str__(self):
        return f"<domain_name={self.domain_name}, zone={self.zone}>"

    class Meta:
        db_table = 'domain_name_dependencies'
        primary_key = CompositeKey('domain_name', 'zone')


class DirectZoneAssociation(BaseModel):
    domain_name = ForeignKeyField(DomainNameEntity)
    zone = ForeignKeyField(ZoneEntity, null=True)

    def __str__(self):
        return f"<domain_name={self.domain_name}, zone={self.zone}>"

    class Meta:
        db_table = 'direct_zone'
        primary_key = CompositeKey('domain_name', 'zone')


class MailDomainComposedAssociation(BaseModel):
    mail_domain = ForeignKeyField(MailDomainEntity)
    mail_server = ForeignKeyField(MailServerEntity)

    def __str__(self):
        return f"<mail_domain={self.mail_domain}, mail_server={self.mail_server}>"

    class Meta:
        db_table = 'mail_domain_composed'
        primary_key = CompositeKey('mail_domain', 'mail_server')


class ScriptWithdrawAssociation(BaseModel):
    script = ForeignKeyField(ScriptEntity, null=True)
    web_site = ForeignKeyField(WebSiteEntity)       # era null=True
    integrity = CharField(null=True)
    https = BooleanField(null=False)

    def __str__(self):
        return f"<script={self.script}, web_site={self.web_site}, integrity={self.integrity}, https={self.https}>"

    class Meta:
        db_table = 'script_withdraw'
        primary_key = CompositeKey('script', 'web_site', 'https')


class ScriptHostedOnAssociation(BaseModel):
    script_site = ForeignKeyField(ScriptSiteEntity)
    script = ForeignKeyField(ScriptEntity)

    def __str__(self):
        return f"<script_site={self.script_site}, script={self.script}>"

    class Meta:
        db_table = 'script_hosted_on'
        primary_key = CompositeKey('script_site', 'script')


class ScriptSiteLandsAssociation(BaseModel):
    script_site = ForeignKeyField(ScriptSiteEntity)
    script_server = ForeignKeyField(ScriptServerEntity, null=True)
    https = BooleanField(null=False)

    def __str__(self):
        return f"<script_site={self.script_site}, script_server={self.script_server}, https={self.https}>"

    class Meta:
        db_table = 'script_site_lands'
        primary_key = CompositeKey('script_site', 'script_server', 'https')


class AccessAssociation(BaseModel):
    domain_name = ForeignKeyField(DomainNameEntity)
    ip_address = ForeignKeyField(IpAddressEntity, null=True)

    def __str__(self):
        return f"<domain_name={self.domain_name}, ip_address={self.ip_address}>"

    class Meta:
        db_table = 'access'


class IpAddressDependsAssociation(BaseModel):
    ip_address = ForeignKeyField(IpAddressEntity)
    ip_network = ForeignKeyField(IpNetworkEntity)
    ip_range_tsv = ForeignKeyField(IpRangeTSVEntity, null=True)
    ip_range_rov = ForeignKeyField(IpRangeROVEntity, null=True)

    def __str__(self):
        return f"<ip_address={self.ip_address}, ip_network={self.ip_network}, ip_range_tsv={self.ip_range_tsv}, ip_range_rov={self.ip_range_rov}>"

    class Meta:
        db_table = 'ip_address_depends'
        primary_key = CompositeKey('ip_address', 'ip_network', 'ip_range_tsv', 'ip_range_rov')


class PrefixesTableAssociation(BaseModel):
    ip_range_rov = ForeignKeyField(IpRangeROVEntity)
    rov = ForeignKeyField(ROVEntity)
    autonomous_system = ForeignKeyField(AutonomousSystemEntity)

    def __str__(self):
        return f"<autonomous_system={self.autonomous_system}, ip_range_rov={self.ip_range_rov}, rov={self.rov}>"

    class Meta:
        db_table = 'prefixes_table'
        primary_key = CompositeKey('ip_range_rov', 'rov', 'autonomous_system')


class NetworkNumbersAssociation(BaseModel):
    ip_range_tsv = ForeignKeyField(IpRangeTSVEntity)
    autonomous_system = ForeignKeyField(AutonomousSystemEntity)      # era null=True

    def __str__(self):
        return f"<ip_range_tsv={self.ip_range_tsv}, autonomous_system={self.autonomous_system}>"

    class Meta:
        db_table = 'network_numbers'


class WebSiteDomainNameAssociation(BaseModel):
    domain_name = ForeignKeyField(DomainNameEntity)
    web_site = ForeignKeyField(WebSiteEntity)

    def __str__(self):
        return f"<web_site={self.web_site}, domain_name={self.domain_name}>"

    class Meta:
        db_table = 'web_site_domain_name'
        primary_key = CompositeKey('web_site', 'domain_name')


class ScriptSiteDomainNameAssociation(BaseModel):
    domain_name = ForeignKeyField(DomainNameEntity)
    script_site = ForeignKeyField(ScriptSiteEntity)

    def __str__(self):
        return f"<script_site={self.script_site}, domain_name={self.domain_name}>"

    class Meta:
        db_table = 'script_site_domain_name'
        primary_key = CompositeKey('script_site', 'domain_name')


class AliasToZoneAssociation(BaseModel):
    domain_name = ForeignKeyField(DomainNameEntity)
    zone = ForeignKeyField(ZoneEntity)

    def __str__(self):
        return f"<zone={self.zone}, domain_name={self.domain_name}>"

    class Meta:
        db_table = 'alias_to_zone'
        primary_key = CompositeKey('zone', 'domain_name')


handle_tables_creation()
