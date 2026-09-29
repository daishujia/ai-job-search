from . import cellxgene, huggingface, massive, pdc, pride, s3, synapse, urls, zenodo

CONNECTORS = {
    "pride": pride.list_files,
    "pdc": pdc.list_files,
    "s3": s3.list_files,
    "huggingface": huggingface.list_files,
    "zenodo": zenodo.list_files,
    "cellxgene": cellxgene.list_files,
    "massive": massive.list_files,
    "urls": urls.list_files,
    "synapse": synapse.list_files,
}
