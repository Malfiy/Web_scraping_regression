import numpy as np
import tensorflow as tf
from tensorflow.keras.layers.experimental.preprocessing import TextVectorization


epochs = 250
loss_func = 'mean_squared_logarithmic_error'
ds_filename = 'dataset3in1.txt'
val_split = 0.2
learning_rate = 0.001
max_features = 2000
seq_len = 200
embedding_dim = 32


def load_dataset(filename):
    with open(filename, 'r') as f:
        return [line.rstrip().split('|') for line in f.readlines()]


ds = load_dataset(ds_filename)
req = [ds[i][0] for i in range(len(ds))]

vec_layer = TextVectorization(
    max_tokens=max_features,
    output_mode='int',
    output_sequence_length=200
)
vec_layer.adapt(req)
train_features = vec_layer(req)
train_labels = np.array([float(int(ds[i][1])) for i in range(len(ds))])

model = tf.keras.Sequential([
    tf.keras.layers.Embedding(max_features + 1, embedding_dim),
    tf.keras.layers.Dense(128, activation='relu'),
    tf.keras.layers.Dense(128, activation='relu'),
    tf.keras.layers.Dense(1)
])

model.compile(loss=loss_func,
              optimizer=tf.keras.optimizers.Adam(learning_rate))


# print(model.predict(train_features))

history = model.fit(
    train_features,
    train_labels,
    validation_split=val_split,
    verbose=0, epochs=epochs)

print(model.predict(train_features))
print(*[(history.history['loss'][i], history.history['val_loss'][i])
        for i in range(len(history.history['loss']))], sep='\n')


def get_salary(description):
    description = description.lower()
    return np.mean(model.predict(vec_layer([description]))[:len(description.split(' '))])


print(get_salary('профессор информатика индекс Хирша по РИНЦ Web of Science Core Collection или Scopus не ниже 1 '
                 'наличие ученой степени доктора наук хабилитация или документы подтверждающие присуждение ученой '
                 'степени и или ученого звания, полученного в иностранном государстве и признаваемого в РФ на уровне '
                 'доктора наук или профессора на момент подачи документов стаж научно-педагогической работы не '
                 'менее 5 лет или ученое звание профессора количество грантов (договоров) за период не ранее '
                 '01.01.2018г в которых претендент являлся либо руководителем либо исполнителем  не менее 1 наличие '
                 'удостоверения о повышении квалификации в области педагогики и/или информационно-коммуникационных '
                 'технологий и/или по области знаний и/или опыт работы от 6 месяцев в иностранных учебных и/или '
                 'научных организациях и/или опыт работы от 6 месяцев в иностранных компаниях на должностях, '
                 'связанных с областью знаний, за период не ранее 01.01.2016г.'))
