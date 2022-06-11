
const Joi = require('joi')

export const fileKeyValidator = (obj) => {
  const schema = Joi.object({
    fileKey: Joi.object().required().messages({
      'object.base': 'Файл носія не обрано'
    }),
    password: Joi.string().min(0).required().messages({
      'string.empty': 'Введіть пароль'
    })
  })
    .options({ abortEarly: false })
  return schema.validate(obj)
}

export const hardwareKeyValidator = (obj) => {
  const schema = Joi.object({
    type: Joi.object().required().messages({
      'object.base': 'Тип ключа не обрано'
    }),
    device: Joi.object().required().messages({
      'object.base': 'Носій ключової інформації не обрано'
    }),
    password: Joi.string().min(0).required().messages({
      'string.empty': 'Введіть пароль'
    })
  })
    .options({ abortEarly: false })
  return schema.validate(obj)
}
