from flask import Flask, render_template, request, redirect, url_for
import csv
from collections import defaultdict

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def index():
    results = []
    if request.method == 'POST':
        file = request.files.get('datafile')
        if file:
            file_content = file.read().decode('utf-8').splitlines()
            reader = csv.reader(file_content, delimiter='~')

            data = defaultdict(lambda: defaultdict(list))
            for row in reader:
                if len(row) < 12:
                    continue
                device = row[6]
                port = row[7]
                try:
                    rssi = int(row[8])
                    stat = float(row[11])
                    data[device][port].append((rssi, stat))
                except ValueError:
                    continue

            for device in sorted(data):
                total_reads = sum(len(entries) for entries in data[device].values())
                for port in sorted(data[device], key=lambda x: int(x)):
                    entries = data[device][port]
                    count = len(entries)
                    percent = (count / total_reads) * 100 if total_reads > 0 else 0
                    avg_rssi = sum(r for r, _ in entries) / count
                    avg_stat = sum(s for _, s in entries) / count
                    strong = len([r for r, _ in entries if 0 >= r > -50])
                    good = len([r for r, _ in entries if -50 >= r > -65])
                    weak = len([r for r, _ in entries if -65 >= r >= -99])
                    results.append({
                        'device': device,
                        'port': port,
                        'count': count,
                        'percent': f"{percent:.1f}%",
                        'avg_rssi': f"{avg_rssi:.1f}",
                        'avg_stat': f"{avg_stat:.1f}",
                        'strong': f"{strong} ({strong / count * 100:.1f}%)",
                        'good': f"{good} ({good / count * 100:.1f}%)",
                        'weak': f"{weak} ({weak / count * 100:.1f}%)"
                    })

    return render_template('index.html', results=results)

if __name__ == '__main__':
    app.run(debug=True)
