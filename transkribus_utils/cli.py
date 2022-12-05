import click
from transkribus_utils import ACDHTranskribusUtils


@click.command()
@click.option("-f", "--file-path", help="Path of the file containing the file titles")
@click.option("-r", "--regex", default=None, help="Regex for creation of collections")
@click.option("-c", "--colid", default=None, help="Collectionid for uploading the docs")
@click.option("--user", default=None, help="Transkribus user if not specified in Env")
@click.option(
    "--password", default=None, help="Transkribus password if not specified in Env"
)
@click.option(
    "--transkribus-base-url",
    default=None,
    help="Transkribus base URL if not specified in Env",
)
@click.option(
    "--goobi-base-url",
    default=None,
    help="Goobi viewer base url if not specified in Env",
)
def import_goobi_mets_to_transkribus(
    file_path,
    regex=None,
    colid=None,
    user=None,
    password=None,
    transkribus_base_url=None,
    goobi_base_url=None,
):
    transkr_utils = ACDHTranskribusUtils(
        user=user,
        password=password,
        transkribus_base_url=transkribus_base_url,
        goobi_base_url=goobi_base_url,
    )
    with open(file_path, "r") as inp:
        inp_lns = [x.strip() for x in inp.readlines()]
        if regex is not None:
            transkr_utils.upload_mets_files_from_goobi(inp_lns, col_regex=regex)
        elif colid is not None:
            transkr_utils.upload_mets_files_from_goobi(inp_lns, col_id=colid)
        else:
            raise AttributeError("You need to either specify a regex or a collectionid")


if __name__ == "__main__":
    import_goobi_mets_to_transkribus()
