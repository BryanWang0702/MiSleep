# Preprocessing the signals, contains artifact rejection

def reject_artifact(midata, methods, threshold):
    """Currently use Raphael's algorithm --- yasa.art_detect

    Parameters
    ----------
    midata : MiData
        data to do rejection
    methods : str, optional
        yasa.art_detect method, {'covar', 'std'}. Defatul is 'std'
    threshold : int, optional
        yasa.art_detect threshold, channels to consideration
    """

