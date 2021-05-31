import logging

from torch import nn

from src.federated.components import testers, client_selectors, aggregators, optims, trainers
from libs.model.linear.lr import LogisticRegression
from src.data import data_generator
from src.data.data_provider import PickleDataProvider
from src.federated import plugins
from src.federated.federated import Events, FederatedLearning
from src.federated.trainer_manager import TrainerManager, SeqTrainerManager

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('main')

data_file = "../datasets/pickles/continuous_balanced.pkl"
test_file = '../datasets/pickles/test_data.pkl'

logger.info('generating data --Started')

dg = data_generator.load(data_file)
client_data = dg.distributed
dg.describe()

trainer_manager = SeqTrainerManager(trainers.CPUChunkTrainer, batch_size=8, epochs=10, criterion=nn.CrossEntropyLoss(),
                                    optimizer=optims.sgd(0.1))

federated = FederatedLearning(
    trainer_manager=trainer_manager,
    aggregator=aggregators.AVGAggregator(),
    tester=testers.Normal(batch_size=8, criterion=nn.CrossEntropyLoss()),
    client_selector=client_selectors.All(),
    trainers_data_dict=client_data,
    initial_model=lambda: LogisticRegression(28 * 28, 10),
    num_rounds=0,
    desired_accuracy=0.99
)

federated.plug(plugins.FederatedLogger([Events.ET_ROUND_FINISHED, Events.ET_TRAINER_SELECTED]))
federated.plug(plugins.FederatedTimer([Events.ET_ROUND_START, Events.ET_TRAIN_END]))
federated.plug(plugins.CustomModelTestPlug(PickleDataProvider(test_file).collect().as_tensor(), 8))
federated.plug(plugins.FedPlot())

logger.info("----------------------")
logger.info("start federated")
logger.info("----------------------")
federated.start()