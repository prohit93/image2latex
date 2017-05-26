from utils.dataset import Dataset
from models.model import Model
from configs.config import Config
from utils.preprocess import greyscale, get_form_prepro


from utils.data_utils import minibatches, pad_batch_formulas, \
    pad_batch_images


if __name__ == "__main__":
    # Load config
    config = Config()

    # Load datasets
    train_set =  Dataset(path_formulas=config.path_formulas, dir_images=config.dir_images,
                    path_matching=config.path_matching_train, img_prepro=greyscale, 
                    form_prepro=get_form_prepro(config.vocab), max_len=config.max_length_formula)

    val_set   =  Dataset(path_formulas=config.path_formulas, dir_images=config.dir_images,
                    path_matching=config.path_matching_val, img_prepro=greyscale, 
                    form_prepro=get_form_prepro(config.vocab), max_len=config.max_length_formula,
                    max_iter=config.max_iter)

    # val_set   =  Dataset(path_formulas=config.path_formulas, dir_images=config.dir_images,
    #                 path_matching=config.path_matching_val, img_prepro=greyscale, 
    #                 form_prepro=get_form_prepro(config.vocab), max_len=50,
    #                 max_iter=config.max_iter)

    # Build model
    model = Model(config)
    model.build()
    model.train(train_set, val_set)