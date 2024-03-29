import esphome.codegen as cg
import esphome.config_validation as cv
from esphome.components import display, i2c, sensor, number
from esphome.const import (
    CONF_LAMBDA,
    CONF_INTENSITY,
    CONF_INVERTED,
    CONF_LENGTH,
    CONF_ID,
)

CONF_INTENSITY_SOURCE_ID = "intensity_source_id"

ht16k33v110_ns = cg.esphome_ns.namespace("ht16k33v110")
HT16K33V110Display = ht16k33v110_ns.class_("HT16K33V110Display", cg.PollingComponent, i2c.I2CDevice)
HT16K33V110DisplayRef = HT16K33V110Display.operator("ref")

def validate_intensity(config):
    if (CONF_INTENSITY_SOURCE_ID in config and CONF_INTENSITY in config):
        raise cv.Invalid(
          f"Do not specify {CONF_INTENSITY} when using {CONF_INTENSITY_SOURCE_ID}"
        )
    return config

HT16K33V110_SCHEMA = cv.Schema(
    display.BASIC_DISPLAY_SCHEMA
    .extend(
        {
            cv.GenerateID(): cv.declare_id(HT16K33V110Display),
            cv.Optional(CONF_INTENSITY, default=7): cv.All(
                cv.uint8_t, cv.Range(min=1, max=16)
            ),
            cv.Optional(CONF_INVERTED, default=False): cv.boolean,
            cv.Optional(CONF_INTENSITY_SOURCE_ID): cv.use_id(number.Number),
        }
    )
    .extend(i2c.i2c_device_schema(0x70))
    .extend(cv.polling_component_schema("1s"))
)

CONFIG_SCHEMA = cv.All(validate_intensity, HT16K33V110_SCHEMA)


async def to_code(config):
    var = cg.new_Pvariable(config[CONF_ID])
    # not needed line after ESPHome 2023.12.0 (?)
    #await cg.register_component(var, config) 
    await display.register_display(var, config)
    await i2c.register_i2c_device(var, config)

    cg.add(var.set_intensity(config[CONF_INTENSITY]))
    cg.add(var.set_inverted(config[CONF_INVERTED]))
    if CONF_INTENSITY_SOURCE_ID in config:
        cg.add(var.set_intensity_auto())
        #cg.add(var.set_intensity_number_id(config[CONF_INTENSITY_SOURCE_ID]))

        intensity_number = await cg.get_variable(config[CONF_INTENSITY_SOURCE_ID])
        cg.add(var.set_intensity_number_id(intensity_number))

    if CONF_LAMBDA in config:
        lambda_ = await cg.process_lambda(
            config[CONF_LAMBDA], [(HT16K33V110DisplayRef, "it")], return_type=cg.void
        )
        cg.add(var.set_writer(lambda_))
