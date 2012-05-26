# A set of functions to be linked using signals

def delete_file_on_model_delete(sender, instance, **kargs):
    file = getattr(instance, 'file', None)
    if file:
        file.delete()
