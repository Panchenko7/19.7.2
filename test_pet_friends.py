from api import PetFriends
from settings import valid_email,valid_password,invalid_email,invalid_password
import os
from requests_toolbelt.multipart.encoder import MultipartEncoder

pf = PetFriends()

def test_get_api_key_for_valid_user(email=valid_email,password=valid_password):
    status, result=pf.get_key(email, password)
    assert status == 200
    assert 'key' in result

def test_get_pet_list_with_valid_key(filter=''):
    _, auth_key = pf.get_key(valid_email, valid_password)
    status, result = pf.get_pet_list(auth_key, filter)
    assert status == 200
    assert len(result['pets'])>0

def test_add_new_pet_with_valid_key(name='Барсик',animal_type='кот',age='1',pet_photo='pexels-pixabay-45201.jpg'):
    pet_photo = os.path.join(os.path.dirname(__file__), pet_photo)
    _, auth_key = pf.get_key(valid_email, valid_password)
    status, result = pf.add_new_pet(auth_key, name, animal_type, age, pet_photo)
    assert status == 200
    assert result['name'] == name

def test_test_successful_delete_self_pet():
    """Проверяем возможность удаления питомца"""
    # Получаем ключ auth_key и запрашиваем список своих питомцев
    _, auth_key = pf.get_key(valid_email, valid_password)
    _, my_pets = pf.get_pet_list(auth_key, "my_pets")
    # Проверяем - если список своих питомцев пустой, то добавляем нового и опять запрашиваем список своих питомцев
    _, auth_key = pf.get_key(valid_email, valid_password)
    _, my_pets = pf.get_pet_list(auth_key,"my_pets")  # Получаем правильный ключ auth_key и запрашиваем список своих питомцев
    if len(my_pets['pets']) == 0:  # если у меня нет никаких питомцев, добавляем питомца
        pf.add_new_pet(auth_key, 'Барсик', 'Кот', 1, 'pexels-pixabay-45201.jpg')
        _, my_pets = pf.get_pet_list(auth_key, "my_pets")  # снова получаем список питомцев - он будет один

    pet_id = my_pets['pets'][0]['id']  # достаем идентификатор последнего добавленного питомца - через словарь
    status, _ = pf.delete_pet(auth_key, pet_id)

    # Ещё раз запрашиваем список своих питомцев
    _, my_pets = pf.get_pet_list(auth_key, "my_pets")

    # Проверяем что статус ответа равен 200 и в списке питомцев нет id удалённого питомца
    assert status == 200
    for i in my_pets['pets']:
        assert pet_id not in i.values()

def test_update_pet(name='Барбос',animal_type='собака',age='6'):
    _, auth_key = pf.get_key(valid_email, valid_password) # получаем ключ
    _, my_pets = pf.get_pet_list(auth_key, "my_pets")      # получаем список питомцев
    if len(my_pets['pets']) > 0: # проверяем, есть ли животные в моем списке
        status, result = pf.update_pet_info(auth_key, my_pets['pets'][0]['id'], name, animal_type, age) # выполняем метод обновления инфы

        assert status == 200
        assert result['name'] == name
    else:
        raise Exception("There is no my pets")



# проверяем возможность входа с неверным паролем
def test_get_api_key_for_invalid_password(email=valid_email,password=invalid_password):
    status, result=pf.get_key(email, password)
    assert status == 403

# проверяем возможность добавления питомца с неверным ключом
def test_add_new_pet_with_invalid_key(name='Барсик',animal_type='Кот',age='1',pet_photo='pexels-pixabay-45201.jpg'):
    pet_photo = os.path.join(os.path.dirname(__file__), pet_photo)
    _, auth_key = pf.get_key(valid_email, valid_password)
    auth_key = auth_key+'a'
    status,result = pf.add_new_pet(auth_key, name, animal_type, age, pet_photo)
    assert status == 403

# проверяем возможность удаления питомца с неверным ключом
    def test_successful_delete_self_pet_with_invalid_key():
        _, auth_key = pf.get_key(valid_email, valid_password)
        _, my_pets = pf.get_pet_list(auth_key, "my_pets")  # Получаем правильный ключ auth_key и запрашиваем список своих питомцев
        if len(my_pets['pets']) == 0: # если у меня нет никаких питомцев, добавляем питомца
            pf.add_new_pet(auth_key,'Барсик', 'Кот','1','pexels-pixabay-45201.jpg')
            _, my_pets = pf.get_pet_list(auth_key, "my_pets")  # снова получаем список питомцев - он будет один

        pet_id = my_pets['pets'][0]['id']  # достаем идентификатор последнего добавленного питомца - через словарь
        auth_key = auth_key + 'a' # "портим" ключ
        status, _ = pf.delete_pet(auth_key, pet_id)  # получаем статус-код ответа на запрос удаления питомца с испорченным ключом
        assert status == 403
        # проверяем, что id питомца остался в базе
        for i in my_pets['pets']:
            assert pet_id  in i.values()

# проверяем возможность добавления питомца без имени
def test_add_new_pet_without_name(animal_type='Кот',age='1',pet_photo='pexels-pixabay-45201.jpg'):
    pet_photo = os.path.join(os.path.dirname(__file__), pet_photo)
    _, auth_key = pf.get_key(valid_email, valid_password)
    status, result = pf.add_new_pet(auth_key, animal_type, age, pet_photo)
    assert status == 400

# проверяем возможность добавления питомца без типа
def test_add_new_pet_without_animal_type(name='Барсик',age='1',pet_photo='pexels-pixabay-45201.jpg'):
    pet_photo = os.path.join(os.path.dirname(__file__), pet_photo)
    _, auth_key = pf.get_key(valid_email, valid_password)
    status, result = pf.add_new_pet(auth_key, name, age, pet_photo)
    assert status == 400

# проверяем возможность добавления питомца без возраста
def test_add_new_pet_without_age(name='Барсик',animal_type='Кот',pet_photo='pexels-pixabay-45201.jpg'):
    pet_photo = os.path.join(os.path.dirname(__file__), pet_photo)
    _, auth_key = pf.get_key(valid_email, valid_password)
    status, result = pf.add_new_pet(auth_key, name, animal_type, pet_photo)
    assert status == 400

# проверяем возможность добавления питомца, с очень длинным именем
def test_add_new_pet_with_long_name_lengt(name='Барсик'*100000,animal_type='Кот',age='1',pet_photo='pexels-pixabay-45201.jpg'):
    pet_photo = os.path.join(os.path.dirname(__file__), pet_photo)
    _, auth_key = pf.get_key(valid_email, valid_password)
    status, result = pf.add_new_pet(auth_key, name, animal_type, age, pet_photo)
    assert status == 400

# проверяем возможность добавления питомца, с очень длинным типом
def test_add_new_pet_with_long_animal_type_lengt(name='Барсик', animal_type='Кот'*100000,age='1',pet_photo='pexels-pixabay-45201.jpg'):
    pet_photo = os.path.join(os.path.dirname(__file__), pet_photo)
    _, auth_key = pf.get_key(valid_email, valid_password)
    status, result = pf.add_new_pet(auth_key, name, animal_type, age, pet_photo)
    assert status == 400

# проверяем возможность добавления питомца, с очень длинным возрастом
def test_add_new_pet_with_long_age_lengt(name='Барсик',animal_type='Кот',age='1'*1000000,pet_photo='pexels-pixabay-45201.jpg'):
    pet_photo = os.path.join(os.path.dirname(__file__), pet_photo)
    _, auth_key = pf.get_key(valid_email, valid_password)
    status, result = pf.add_new_pet(auth_key, name, animal_type, age, pet_photo)
    assert status == 400

