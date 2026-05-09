import esphome.codegen as cg
import esphome.config_validation as cv
from esphome.components import i2c, text_sensor
from esphome.const import CONF_ID

DEPENDENCIES = ['i2c', 'text_sensor']

isb_orchestrator_ns = cg.esphome_ns.namespace('isb_orchestrator')
ISBOrchestrator = isb_orchestrator_ns.class_('ISBOrchestrator', cg.Component)

CONF_I2C_ID = 'i2c_id'
CONF_VERSIONS_SENSOR = 'versions_sensor'

CONFIG_SCHEMA = cv.Schema({
    cv.GenerateID(): cv.declare_id(ISBOrchestrator),
    cv.Required(CONF_I2C_ID): cv.use_id(i2c.I2CBus),
    cv.Optional(CONF_VERSIONS_SENSOR): cv.use_id(text_sensor.TextSensor),
}).extend(cv.COMPONENT_SCHEMA)

async def to_code(config):
    var = cg.new_Pvariable(config[CONF_ID])
    await cg.register_component(var, config)
    i2c_bus = await cg.get_variable(config[CONF_I2C_ID])
    cg.add(var.set_i2c_bus(i2c_bus))

    if CONF_VERSIONS_SENSOR in config:
        sens = await cg.get_variable(config[CONF_VERSIONS_SENSOR])
        cg.add(var.set_versions_sensor(sens))
