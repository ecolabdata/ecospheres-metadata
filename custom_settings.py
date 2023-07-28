from itables import init_notebook_mode
import itables.options as opt

def apply_itable_custom_settings():
    """ Allows interactive dataframe presentation
    vie the show function.
    """
    
    opt.lengthMenu = [5, 10]
    opt.style = 'table-layout:auto;width:auto;margin:auto;caption-side:bottom'
    opt.classes = 'display compact'
    opt.scrollY = '300px'