from convNet1 import convModel
from imageLoader import DataLoader
import imgSrc
from utils import getClientsNumber
import os
from utils import generateLatexTabular
devices = getClientsNumber()
proxy = 0.5
test = 0.1

def testParams():
    global devices
    global proxy
    global test
    split_seeds = [50, 101, 202, 303, 404]
    for seed in split_seeds:
        dl = DataLoader(mainPath=imgSrc.covid_dataset, classDirs=imgSrc.covid_classes, split=test, seed=seed, devices=devices, proxySplit=proxy)
        dl.splitData()

        dl.plotClasses(imgSrc.results)
        cr, r = dl.countClasses()
        generateLatexTabular(cr, r, savePath=os.path.join(imgSrc.results, 'class_distribution_tabular_seed_' + str(seed) + '.txt'))


def trainProxyModels(epohs=50):
    models = ('vgg', 'inc', 'res')
    proxyModel = convModel()

    for model in models:
        proxyModel.setNet(model)
        proxyModel.getLayersInfo(imgSrc.results)
        proxyModel.trainModel(epohs=epohs)
        proxyModel.getConfusionMatrix(imgSrc.results)
        proxyModel.learningCurves(imgSrc.results)
        proxyModel.saveModelToFile(model)

# testParams()

# dl = DataLoader(mainPath=imgSrc.covid_dataset, classDirs=imgSrc.covid_classes, split=test, seed=303, devices=devices, proxySplit=proxy)
# dl.splitData()

# trainProxyModels()