if __package__ is None or __package__ == '':
    # uses current directory visibility
    import getSermons
    import passage
    import sermon
else:
    # uses current package visibility
    from . import getSermons
    from . import passage
    from . import sermon