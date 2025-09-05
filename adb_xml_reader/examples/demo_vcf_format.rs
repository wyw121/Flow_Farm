use adb_xml_reader::vcf_import::{VcfImporter, Contact};

#[tokio::main]
async fn main() -> anyhow::Result<()> {
    println!("🎯 演示完整的VCF联系人导入流程...");
    println!("{}", "=".repeat(60));

    // 读取测试联系人文件
    let contacts_file = "D:\\repositories\\employeeGUI\\test_contacts.txt";
    let contacts = VcfImporter::read_contacts_from_file(contacts_file)?;

    println!("📋 从文件读取到 {} 个联系人:", contacts.len());
    for (i, contact) in contacts.iter().enumerate() {
        println!("  {}. {} - {}", i + 1, contact.name, contact.phone);
    }

    // 生成VCF文件
    VcfImporter::generate_vcf_file(&contacts, "demo_contacts.vcf")?;

    // 显示第一个联系人的VCF格式
    if let Some(first_contact) = contacts.first() {
        println!("\n📄 第一个联系人的VCF格式:");
        println!("{}", "-".repeat(40));
        println!("{}", first_contact.to_vcf());
    }

    // 读取并显示完整VCF文件（前500个字符）
    let vcf_content = std::fs::read_to_string("demo_contacts.vcf")?;
    println!("📄 完整VCF文件内容 (前500个字符):");
    println!("{}", "-".repeat(40));
    let preview = if vcf_content.len() > 500 {
        format!("{}...\n[文件总长度: {} 字符]", &vcf_content[..500], vcf_content.len())
    } else {
        vcf_content.clone()
    };
    println!("{}", preview);

    println!("\n✅ 演示完成！");
    println!("📁 生成的文件: demo_contacts.vcf");
    println!("📖 VCF文件遵循RFC 6350标准，兼容所有主流联系人应用");

    Ok(())
}
