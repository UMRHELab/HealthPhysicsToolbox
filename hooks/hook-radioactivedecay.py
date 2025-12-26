from PyInstaller.utils.hooks import collect_data_files, collect_submodules
datas = collect_data_files('radioactivedecay')
hidden_imports = collect_submodules('radioactivedecay')  + [
    'numpy', 'numpy.core._multiarray_umath', 'numpy.core.multiarray'
]