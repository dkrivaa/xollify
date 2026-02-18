""" This is used to initialize registry of all chains at startup """

from backend.app.core.binaprojects import BinaProjects
from backend.app.core.carrefour import CarrefourParent
# from backend.app.core.hazihinam import HaziHinam
# from backend.app.core.laibcatalog import LaibCatalog
from backend.app.core.publishedprices import PublishedPrices
from backend.app.core.shufersal import Shufersal
from backend.app.core.super_class import SupermarketChain


def initialize_backend():
    """
    Call this once at app startup.
    Ensures all supermarket chains subclasses are imported and registered.
    """
    # print("Registered chains:", SupermarketChain.registry)
    pass



