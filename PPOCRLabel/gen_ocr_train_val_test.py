# coding:utf8
import os
import shutil
import random
import argparse


# Delete the divided train, val, and test folders and create a new empty folder
def isCreateOrDeleteFolder(path, flag):
    flagPath = os.path.join(path, flag)

    if os.path.exists(flagPath):
        shutil.rmtree(flagPath)

    os.makedirs(flagPath)
    flagAbsPath = os.path.abspath(flagPath)
    return flagAbsPath


def splitTrainVal(
    root,
    abs_train_root_path,
    abs_val_root_path,
    abs_test_root_path,
    train_txt,
    val_txt,
    test_txt,
    flag,
):
    data_abs_path = os.path.abspath(root)
    label_file_name = args.detLabelFileName if flag == "det" else args.recLabelFileName
    label_file_path = os.path.join(data_abs_path, label_file_name)

    with open(label_file_path, "r", encoding="UTF-8") as label_file:
        label_file_content = label_file.readlines()
        random.shuffle(label_file_content)
        label_record_len = len(label_file_content)

        for index, label_record_info in enumerate(label_file_content):
            image_relative_path, image_label = label_record_info.split("\t")
            image_name = os.path.basename(image_relative_path)

            if flag == "det":
                image_path = os.path.join(data_abs_path, image_name)
            elif flag == "rec":
                image_path = os.path.join(
                    data_abs_path, args.recImageDirName, image_name
                )

            train_val_test_ratio = args.trainValTestRatio.split(":")
            train_ratio = eval(train_val_test_ratio[0]) / 10
            val_ratio = train_ratio + eval(train_val_test_ratio[1]) / 10
            cur_ratio = index / label_record_len

            if cur_ratio < train_ratio:
                image_copy_path = os.path.join(abs_train_root_path, image_name)
                shutil.copy(image_path, image_copy_path)
                train_txt.write("{}\t{}".format(image_copy_path, image_label))
            elif cur_ratio >= train_ratio and cur_ratio < val_ratio:
                image_copy_path = os.path.join(abs_val_root_path, image_name)
                shutil.copy(image_path, image_copy_path)
                val_txt.write("{}\t{}".format(image_copy_path, image_label))
            else:
                image_copy_path = os.path.join(abs_test_root_path, image_name)
                shutil.copy(image_path, image_copy_path)
                test_txt.write("{}\t{}".format(image_copy_path, image_label))


# Remove the file if it exists
def removeFile(path):
    if os.path.exists(path):
        os.remove(path)


def genDetRecTrainVal(args):
    detAbsTrainRootPath = isCreateOrDeleteFolder(args.detRootPath, "train")
    detAbsValRootPath = isCreateOrDeleteFolder(args.detRootPath, "val")
    detAbsTestRootPath = isCreateOrDeleteFolder(args.detRootPath, "test")
    recAbsTrainRootPath = isCreateOrDeleteFolder(args.recRootPath, "train")
    recAbsValRootPath = isCreateOrDeleteFolder(args.recRootPath, "val")
    recAbsTestRootPath = isCreateOrDeleteFolder(args.recRootPath, "test")

    removeFile(os.path.join(args.detRootPath, "train.txt"))
    removeFile(os.path.join(args.detRootPath, "val.txt"))
    removeFile(os.path.join(args.detRootPath, "test.txt"))
    removeFile(os.path.join(args.recRootPath, "train.txt"))
    removeFile(os.path.join(args.recRootPath, "val.txt"))
    removeFile(os.path.join(args.recRootPath, "test.txt"))

    detTrainTxt = open(
        os.path.join(args.detRootPath, "train.txt"), "a", encoding="UTF-8"
    )
    detValTxt = open(os.path.join(args.detRootPath, "val.txt"), "a", encoding="UTF-8")
    detTestTxt = open(os.path.join(args.detRootPath, "test.txt"), "a", encoding="UTF-8")
    recTrainTxt = open(
        os.path.join(args.recRootPath, "train.txt"), "a", encoding="UTF-8"
    )
    recValTxt = open(os.path.join(args.recRootPath, "val.txt"), "a", encoding="UTF-8")
    recTestTxt = open(os.path.join(args.recRootPath, "test.txt"), "a", encoding="UTF-8")

    splitTrainVal(
        args.datasetRootPath,
        detAbsTrainRootPath,
        detAbsValRootPath,
        detAbsTestRootPath,
        detTrainTxt,
        detValTxt,
        detTestTxt,
        "det",
    )

    for root, dirs, files in os.walk(args.datasetRootPath):
        for dir in dirs:
            if dir == "crop_img":
                splitTrainVal(
                    root,
                    recAbsTrainRootPath,
                    recAbsValRootPath,
                    recAbsTestRootPath,
                    recTrainTxt,
                    recValTxt,
                    recTestTxt,
                    "rec",
                )
            else:
                continue
        break


if __name__ == "__main__":
    """
    Function description: Split detection and recognition datasets into training, validation, and test sets
    Note: You can adjust parameters according to your own path and needs. Image data is often annotated
    in batches by multiple people collaborating. Each batch of image data is placed in a folder and
    annotated using PPOCRLabel. This creates a need to aggregate multiple annotated image folders
    and split them into training, validation, and test sets.
    """
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--trainValTestRatio",
        type=str,
        default="8:2:0",
        help="ratio of trainset:valset:testset",
    )
    parser.add_argument(
        "--datasetRootPath",
        type=str,
        default=r"E:\datasets\char",
        help="path to the dataset marked by ppocrlabel, E.g, dataset folder named 1,2,3...",
    )
    parser.add_argument(
        "--detRootPath",
        type=str,
        default=r"E:\datasets\char",
        help="the path where the divided detection dataset is placed",
    )
    parser.add_argument(
        "--recRootPath",
        type=str,
        default=r"E:\datasets\char",
        help="the path where the divided recognition dataset is placed",
    )
    parser.add_argument(
        "--detLabelFileName",
        type=str,
        default="Label.txt",
        help="the name of the detection annotation file",
    )
    parser.add_argument(
        "--recLabelFileName",
        type=str,
        default="rec_gt.txt",
        help="the name of the recognition annotation file",
    )
    parser.add_argument(
        "--recImageDirName",
        type=str,
        default="crop_img",
        help="the name of the folder where the cropped recognition dataset is located",
    )
    args = parser.parse_args()
    genDetRecTrainVal(args)
