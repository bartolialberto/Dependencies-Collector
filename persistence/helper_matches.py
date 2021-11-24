from persistence import helper_nameserver, helper_entry_ip_as_database, helper_entry_rov_page, helper_ip_network, \
    helper_prefix, helper_belonging_network, helper_range, helper_has
from persistence.BaseModel import EntryIpAsDatabaseEntity, MatchesAssociation, NameserverEntity, EntryROVPageEntity


def insert_or_get_only_entry_ip_as_db(n: NameserverEntity, eia: EntryIpAsDatabaseEntity):
    ma, created = MatchesAssociation.get_or_create(nameserver=n.id, entry_rov_page=None, entry_ip_as_database=eia.id)


def insert_or_get(n: NameserverEntity, eia: EntryIpAsDatabaseEntity, erp: EntryROVPageEntity):
    ma, created = MatchesAssociation.get_or_create(nameserver=n.id, entry_rov_page=erp.id, entry_ip_as_database=eia.id)


def insert_or_get_only_entry_rov_page(nameserver: str, e: EntryROVPageEntity):
    n = NameserverEntity.get(NameserverEntity.name == nameserver)
    ma = MatchesAssociation.get(MatchesAssociation.nameserver == n.id)
    ma.entry_rov_page = e.id
    ma.save()


def insert_all_entries_associated(all_entries_result_by_as: dict):
    for as_number in all_entries_result_by_as.keys():
        for nameserver in all_entries_result_by_as[as_number].keys():
            #
            ip_string = all_entries_result_by_as[as_number][nameserver][0]
            entry_ip_as_db = all_entries_result_by_as[as_number][nameserver][1]
            belonging_network_ip_as_db = all_entries_result_by_as[as_number][nameserver][2]
            entry_rov_page = all_entries_result_by_as[as_number][nameserver][3]
            #
            ns = helper_nameserver.insert_or_get(nameserver, ip_string)
            eia = helper_entry_ip_as_database.insert_or_get(entry_ip_as_db)
            r = helper_range.insert_or_get(entry_ip_as_db.start_ip_range, entry_ip_as_db.end_ip_range)
            h = helper_has.insert_or_get(eia, r)
            if entry_rov_page is None:
                insert_or_get_only_entry_ip_as_db(ns, eia)
            else:
                erp = helper_entry_rov_page.insert(entry_rov_page)
                insert_or_get(ns, eia, erp)
                nrps = helper_ip_network.insert_or_get(entry_rov_page.prefix)
                helper_prefix.insert(erp, nrps)
            niad = helper_ip_network.insert_or_get(belonging_network_ip_as_db)
            helper_belonging_network.insert_or_get(entry_ip_as_db.as_number, niad)
