import hashlib
# A set of functions to be linked using signals

def delete_file_on_model_delete(sender, instance, **kargs):
    file = getattr(instance, 'file', None)
    if file:
        file.delete(save=False)

def generate_md5_sum(file_object):
    if file_object:
        md5 = hashlib.md5()
        file_object.open('rb')
        for chunk in file_object.chunks():
            md5.update(chunk)
        return md5.hexdigest()
    return None

