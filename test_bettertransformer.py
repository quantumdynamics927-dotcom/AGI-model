try:
    from transformers import BetterTransformer
    print('BetterTransformer found in transformers')
except ImportError as e:
    print('BetterTransformer not in transformers:', e)