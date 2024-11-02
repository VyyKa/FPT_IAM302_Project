def save_results(results, output_file):
    """Save the prediction results along with static and dynamic analysis to a file."""
    with open(output_file, 'w') as f:
        for result in results:
            f.write(f"Prediction: {result['prediction']}\n")
            f.write("Static Analysis:\n")
            for key, value in result['static_analysis'].items():
                f.write(f"  {key}: {value}\n")
            f.write("Behaviors Detected:\n")
            for behavior in result['behaviors']:
                f.write(f"  {behavior['name']} (Severity: {behavior['severity']}): {behavior['description']}\n")
            f.write("\n")
    print(f"Results saved to {output_file}")
