"""
Функции расчета резистентности
"""

from abstracts import Calculator
from config import settings
from methods.AMRDirect.db import database_handler


class AMRDirectCalculator(Calculator):
    def convert_validated_data(self, data):
        if hasattr(data[0]['variable'], 'name') and hasattr(data[0]['result'], 'value'):  # TODO deal with it
            return {datum['variable'].name: datum['result'].value for datum in data}
        else:
            return {datum['variable']: datum['result'] for datum in data}

    def _calculate_direct_amr(self, data=None, metadata=None):
        """
        Получение списка групп антибиотиков на основе результатов ПЦР.

        :param data: словарь с результатами тестов ПЦР
        :return: словарь с со списком групп антибиотиков для визуализации
        :rtype: dict
        """

        sql_request = """
        SELECT DISTINCT 
            gt.test_id AS test_id,
            dc_name.name AS drug_class_name
        FROM drug_class dc
        LEFT JOIN gene_drug_class gdc ON gdc.drug_class_id = dc.id
        LEFT JOIN gene g ON gdc.gene_id = g.id
        LEFT JOIN gene_test gt ON gt.gene_id = g.id
        LEFT JOIN test_numedy_link tnl on tnl.test_id = gt.test_id
        LEFT JOIN name dc_name ON dc_name.name_string_id = dc.name_string_id
        WHERE dc_name.language_id = 0
        """

        amr_table = database_handler(sql_request)
        validated_data = data
        validated_data = self.convert_validated_data(validated_data)

        for amr in amr_table:
            amr['result'] = validated_data[amr['test_id']] if amr['test_id'] in validated_data.keys() else 0
        result = {}
        for amr in amr_table:
            if amr['drug_class_name'] in result.keys():
                result[amr['drug_class_name']] = max(result[amr['drug_class_name']], amr['result'])
            else:
                result[amr['drug_class_name']] = amr['result']

        # TODO dirty hack bcs most bacteria are sensitive to FA, and the test for FA is not implemented yet
        result['fluoroquinolone_antibiotic'] = max(result['fluoroquinolone_antibiotic'], 1)

        return result

    def calculate(self, data: dict) -> bool:
        self.result = self._calculate_direct_amr(data=data['data'],
                                                 metadata=data['metadata'])
        return True


def calculate_indirect_amr(data=None):  # TODO for future implementation
    """
    Получение списка групп антибиотиков на основе результатов ПЦР биоценозов.

    :param data: словарь с результатами тестов ПЦР
    :return: словарь с со списком групп антибиотиков для визуализации
    :rtype: dict
    """
    return {}
