from pydantic_factories import ModelFactory

from abstracts import Converter, IntermediateData
from data_definitions.errors import ExternalError
from data_definitions.internal_format import InternalFormat
from data_definitions.numedy import InputPackage, OutputPackage, OutputModelImage
from methods.AMRDirect.db import database_handler
from config import settings

include_keys = {
    'id': True,
    'model': {
        'birthday_day': True,
        'birthday_month': True,
        'birthday_year': True,
        'gender_id': True
    },
    'data': {'__all__': {
        'id_': True,
        'measure_time': True,
        'id_result_argument': True,
        'result': True
    }}
}


class AMRDirectConverter(Converter):
    variable_name_collation_request = """
    SELECT tnl.numedy_measurement_id, tnl.test_id
    FROM test_numedy_link tnl
    """

    variable_name_collation = database_handler(variable_name_collation_request)

    # variable_name_collation be like {
    #     '20001': 'oxa_23_like',  # Planned in Numedy
    #     '20002': 'oxa_40_like',  # Planned in Numedy
    #     '20003': 'oxa_58_like',  # Planned in Numedy
    #     '20004': 'vana',  # Planned in Numedy
    #     '20005': 'vanb',  # Planned in Numedy
    #     '20006': 'imp',  # Planned in Numedy
    #     '20007': 'ndm',  # Planned in Numedy
    #     '20008': 'vim',  # Planned in Numedy
    #     '20009': 'oxa_48_like',  # Planned in Numedy
    #     '20010': 'kpc',  # Planned in Numedy
    #     '20011': 'meca',  # Planned in Numedy
    #     '20012': 'oxa_28_like',
    #     '20013': 'ctx_m_1',
    #     '20014': 'ges',
    #     '20015': 'oxa_51_like',
    #     '20016': 'shv',
    #     '20017': 'tem',
    #     '20018': 'mg_ml',
    #     '20019': 'mg_fq',
    #     '20020': 'mef',
    #     '20021': 'ermb',
    #     '20022': 'tetm',
    #     '20023': 'ctx_m_9'
    # }

    variable_name_collation = {e['numedy_measurement_id']: e['test_id'] for e in variable_name_collation}

    variable_value_collation = settings.get('VARIABLE_VALUE_COLLATION')

    def __init__(self):
        self.internal_data = None
        self.input_package = None
        self.output_package = None

    def store(self, input_package: InputPackage) -> bool:
        self.input_package = input_package
        return True

    def convert(self) -> bool:
        metadata = self.input_package.model.dict()
        data = list(map(lambda x: dict(x), self.input_package.data))

        for datablock in data:
            if datablock['id_result_argument'] in self.variable_name_collation:
                datablock['variable'] = self.variable_name_collation[datablock['id_result_argument']]
            else:
                datablock['variable'] = datablock['id_result_argument']

            if datablock['result'] in self.variable_value_collation:
                datablock['result'] = self.variable_value_collation[datablock['result']]

        internal_data = InternalFormat(metadata=metadata, data=data)
        internal_data.remove_expired()
        self.internal_data = internal_data
        return True

    def restore_successful_run(self, method_result: IntermediateData) -> bool:
        internal_data = self.internal_data
        output_data = self.input_package.copy(deep=True)

        processed_uuids = {element.id_ for element in internal_data.data}

        for output_data_block in output_data.data:
            if output_data_block.id_ not in processed_uuids:
                output_data.data.remove(output_data_block)

        for internal_data_block in internal_data.data:
            for output_data_block in output_data.data:
                if internal_data_block.id_ == output_data_block.id_:
                    output_data_block.result = internal_data_block.result

        self.output_package = OutputPackage(**output_data.dict())
        self.output_package.model.image = OutputModelImage(antibiotic_resist=method_result.visualizer_bytes)
        return True
    
    def restore_erroneous_run(self, error: ExternalError) -> bool:
        class OutputFactory(ModelFactory):
            __model__ = OutputPackage

        if self.input_package is not None:
            input_package = self.input_package.copy(deep=True)
            input_package.data = None
            output_package = OutputPackage(**input_package.dict())
            output_package.model.error = error
            self.output_package = output_package
            return True
        else:
            #create empty output_package
            output_package = OutputFactory.build()
            #populate output_package with error
            output_package.model.error = error
            #return output_package
            self.output_package = output_package
            return True
