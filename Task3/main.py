import argparse
import re
import yaml


def parse_input(input_text):
    input_text = re.sub(r'\(comment.*?\)', '', input_text, flags=re.DOTALL).strip()
    data = {}
    lines = input_text.splitlines()

    for line in lines:
        line = line.strip()
        if not line:
            continue

        if match := re.match(r'const\s+([a-zA-Z_]\w*)\s*=\s*(.*)', line):
            const_name, const_value = match.groups()
            data[const_name] = evaluate_expression(const_value, data)
        elif '=' in line:
            key, value = line.split('=', 1)
            key = key.strip()
            value = parse_value(value.strip(), data)
            data[key] = value
        else:
            raise ValueError(f"Неверный синтаксис строки: {line}")

    return data


def evaluate_expression(expression, context):
    expression = re.sub(r'\$(\w+)', lambda x: str(context.get(x.group(1), 0)), expression)
    # Обработка min перед вычислением
    if 'min(' in expression:
        numbers = re.findall(r'\d+', expression)
        return min(map(int, numbers))

    try:
        return eval(expression)
    except Exception as e:
        raise ValueError(f"Ошибка при вычислении выражения: {expression}. {str(e)}")


def parse_value(value, context):
    if value.startswith('[[', 0) and value.endswith(']]'):
        return value[2:-2]
    elif value.startswith('{') and value.endswith('}'):
        return parse_array(value[1:-1])
    elif re.match(r'^[\d]+$', value):
        return int(value)
    elif re.match(r'^[a-zA-Z_]\w*$', value):
        return context.get(value, value)

    raise ValueError(f"Не удалось распарсить значение: {value}")


def parse_array(value):
    return [v.strip() for v in value.split(',')]


def main(input_text, output_file):
    try:
        parsed_data = parse_input(input_text)
        with open(output_file, 'w') as yaml_file:
            yaml.dump(parsed_data, yaml_file, allow_unicode=True)
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Конфигурационный инструмент')
    parser.add_argument('output_file', help='Путь к выходному файлу YAML')
    args = parser.parse_args()

    input_text = ''
    try:
        while True:
            line = input()
            input_text += line + "\n"
    except EOFError:
        pass

    main(input_text, args.output_file)