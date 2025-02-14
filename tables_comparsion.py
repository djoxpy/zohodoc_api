import csv


def parse_file(file: str, type: str) -> set:
    with open(file) as csvfile:
        data = csv.DictReader(csvfile)
        servers = set()
        for row in data:
            if type == "all":
                a = (row["hostname"], row["role"], row["Status"])
                servers.add(a)

            if type == "role":
                a = (row["hostname"], row["role"])
                servers.add(a)

            if type == "status":
                a = (row["hostname"], row["Status"])
                servers.add(a)
        return servers


def print_result(old_file: str, new_file: str, type: str):
    old_set = parse_file(old_file, type)
    new_set = parse_file(new_file, type)

    diff_old = old_set.difference(new_set)
    diff_new = new_set.difference(old_set)

    if type == "all":
        hosts_diff_old = set((i for i, _, _ in diff_old))
        hosts_diff_new = set((i for i, _, _ in diff_new))

    if type == "role" or type == "status":
        hosts_diff_old = set((i for i, _ in diff_old))
        hosts_diff_new = set((i for i, _ in diff_new))

    deleted_hosts = hosts_diff_old.difference(hosts_diff_new)
    added_hosts = hosts_diff_new.difference(hosts_diff_old)
    changed_hosts = hosts_diff_old.intersection(hosts_diff_new)

    # DELETED HOSTS
    deleted_hosts_full_data = []
    for host in deleted_hosts:
        for old in diff_old:
            if host == old[0]:
                deleted_hosts_full_data.append(old)
                break

    deleted_hosts_full_data_msg = []
    for del_host in deleted_hosts_full_data:
        if type == "role":
            msg = "\t\t\t\t__" + "__\n \t\t\t\t🔹role: ".join(del_host)
        if type == "status":
            msg = "\t\t\t\t__" + "__\n \t\t\t\t🔹status: ".join(del_host)
        deleted_hosts_full_data_msg.append(msg)

    # NEW HOSTS
    new_hosts_full_data = []
    for host in added_hosts:
        for new in diff_new:
            if host == new[0]:
                new_hosts_full_data.append(new)
                break

    new_hosts_full_data_msg = []
    for new_host in new_hosts_full_data:
        if type == "role":
            msg = "\t\t\t\t__" + "__\n \t\t\t\t🔹role: ".join(new_host)
        if type == "status":
            msg = "\t\t\t\t__" + "__\n \t\t\t\t🔹status: ".join(new_host)
        new_hosts_full_data_msg.append(msg)

    # CHANGED HOSTS
    changed_hosts_full_data = []
    for host in changed_hosts:
        current = [host]

        if type == "all":
            for new_host, new_role, new_status in diff_new:
                if host == new_host:
                    current.append(new_role)
                    current.append(new_status)
                    break

            for old_host, old_role, old_status in diff_old:
                if host == old_host:
                    current.append(old_role)
                    current.append(old_status)
                    break

        if type == "role" or type == "status":
            for old_host, old_role in diff_old:
                if host == old_host:
                    current.append(old_role)
                    break

            for new_host, new_role in diff_new:
                if host == new_host:
                    current.append(new_role)
                    break

        changed_hosts_full_data.append(tuple(current))

    changed_hosts_full_data_msg = []
    for changed_host in changed_hosts_full_data:
        if type == "role":
            msg = f"\t\t\t\t__{changed_host[0]}__\n \t\t\t\t🔻old   role: \t{changed_host[1]}\n \t\t\t\t🔹new role: \t{changed_host[2]}"
        if type == "status":
            msg = f"\t\t\t\t__{changed_host[0]}__\n \t\t\t\t🔻old   status: \t{changed_host[1]}\n \t\t\t\t🔹new status: \t{changed_host[2]}"
        # Alternative block code view...
        # msg = f"{changed_host[0]}```\nold role:      {changed_host[1]}\nnew role:      {changed_host[2]}```"
        changed_hosts_full_data_msg.append(msg)

    deleted_data_tg_msg = ""
    new_data_tg_msg = ""
    changed_data_tg_msg = ""

    if deleted_hosts_full_data_msg:
        deleted_data_tg_msg = "🔴*DELETED HOSTS:* \n" + "\n".join(
            deleted_hosts_full_data_msg
        )

    if new_hosts_full_data_msg:
        new_data_tg_msg = "🟢*NEW HOSTS:* \n" + "\n".join(new_hosts_full_data_msg)

    if changed_hosts_full_data_msg:
        changed_data_tg_msg = "🟡*CHANGED HOSTS:* \n" + "\n".join(
            changed_hosts_full_data_msg
        )

    return deleted_data_tg_msg + "\n\n" + new_data_tg_msg + "\n\n" + changed_data_tg_msg
